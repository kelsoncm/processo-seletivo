from .models import EventoAuditoria


class AuditMiddleware:
    """
    Middleware que registra acessos autenticados ao sistema na trilha de auditoria.
    """

    EXCLUDED_PATHS = ['/static/', '/media/', '/favicon.ico']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if self._deve_auditar(request):
            usuario = request.user if request.user.is_authenticated else None
            EventoAuditoria.registrar(
                tipo=EventoAuditoria.ACESSO,
                acao=f'{request.method} {request.path}',
                usuario=usuario,
                origem=self._get_ip(request),
            )

        return response

    def _deve_auditar(self, request):
        if not request.user.is_authenticated:
            return False
        for path in self.EXCLUDED_PATHS:
            if request.path.startswith(path):
                return False
        return True

    def _get_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')
