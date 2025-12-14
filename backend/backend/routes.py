def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    
    # API Routes
    config.add_route('get_reviews', '/api/reviews')
    config.add_route('analyze_review', '/api/analyze-review')