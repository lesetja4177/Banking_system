from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/transactions/', include('transactions.urls')),
]

# Serve media files even in production (for testing)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)