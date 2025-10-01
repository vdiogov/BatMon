from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views # Import api_views

app_name = 'monitoring'

router = DefaultRouter()
router.register(r'servicechecks', api_views.ServiceCheckViewSet)
router.register(r'checkresults', api_views.CheckResultViewSet)
router.register(r'alerts', api_views.AlertViewSet)
router.register(r'alertlogs', api_views.AlertLogViewSet)
router.register(r'maintenancewindows', api_views.MaintenanceWindowViewSet)

urlpatterns = [
    path('status/', views.status_page, name='status_page'),
    path('status/<int:service_id>/', views.service_detail, name='service_detail'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('api/', include(router.urls)), # Include API URLs
]