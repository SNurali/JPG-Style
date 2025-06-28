from django.utils.deprecation import MiddlewareMixin

class SEOMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if hasattr(response, 'context_data') and response.context_data:
            response['X-Robots-Tag'] = 'index, follow'
            response['Link'] = f'<{request.build_absolute_uri("/sitemap.xml")}>; rel="sitemap"'
        return response