from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
)

from .meta import Base

class Review(Base):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True)
    product_name = Column(String(255), nullable=True) # Opsional
    review_text = Column(Text, nullable=False)
    sentiment = Column(String(50), nullable=True)     # Positive/Negative/Neutral
    key_points = Column(Text, nullable=True)          # Hasil rangkuman Gemini
    
    def __json__(self, request):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'review_text': self.review_text,
            'sentiment': self.sentiment,
            'key_points': self.key_points
        }