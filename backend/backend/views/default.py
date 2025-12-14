import os
import requests
import google.generativeai as genai
from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy.exc import DBAPIError
from dotenv import load_dotenv
from ..models import Review

# 1. Load API Keys dari file .env
load_dotenv()
HF_API_KEY = os.getenv('HF_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Setup Gemini
genai.configure(api_key=GEMINI_API_KEY)

# --- FUNGSI BANTUAN (HELPER) ---

def get_sentiment_hf(text):
    """Kirim text ke Hugging Face untuk cek sentimen"""
    API_URL = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": text})
        
        # Cek jika error Rate Limit (429) atau Model Loading (503)
        if response.status_code != 200:
            return "Neutral" # Fallback jika error
            
        data = response.json()
        # Hugging Face mengembalikan list of list, kita ambil skor tertinggi
        # Format return: [[{'label': 'positive', 'score': 0.9}, ...]]
        scores = data[0]
        sorted_scores = sorted(scores, key=lambda x: x['score'], reverse=True)
        top_label = sorted_scores[0]['label'] # positive/negative/neutral
        
        return top_label.capitalize() # Ubah jadi huruf besar (Positive)
    except Exception as e:
        print(f"Error HF: {e}")
        return "Neutral"

def get_key_points_gemini(text):
    """Kirim text ke Gemini untuk diringkas"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"Extract 3-5 key points short summary from this product review in Indonesian bullet points: '{text}'"
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error Gemini: {e}")
        return "Gagal mengambil poin penting."

# --- ENDPOINTS ---

@view_config(route_name='home', renderer='json')
def my_view(request):
    return {'status': 'Server Ready', 'message': 'AI Integration Active'}

@view_config(route_name='get_reviews', renderer='json')
def get_reviews_view(request):
    try:
        # Ambil data terbaru dulu (descending order)
        reviews = request.dbsession.query(Review).order_by(Review.id.desc()).all()
        return {'data': reviews}
    except DBAPIError:
        return Response(json_body={'error': 'Database Error'}, status=500)

@view_config(route_name='analyze_review', renderer='json', request_method='POST')
def analyze_review_view(request):
    try:
        payload = request.json_body
        text = payload.get('review_text')
        
        if not text:
            return Response(json_body={'error': 'Review text is required'}, status=400)

        # 1. Panggil AI (Proses ini mungkin butuh 2-3 detik)
        sentiment_result = get_sentiment_hf(text)
        key_points_result = get_key_points_gemini(text)
        
        # 2. Simpan ke Database
        new_review = Review(
            review_text=text,
            sentiment=sentiment_result,
            key_points=key_points_result
        )
        request.dbsession.add(new_review)
        request.dbsession.flush() # Agar ID langsung ter-generate
        
        return {
            'message': 'Analysis Complete',
            'data': new_review # Return data lengkap ke frontend
        }
    except Exception as e:
        return Response(json_body={'error': str(e)}, status=500)