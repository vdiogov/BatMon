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
    path('', views.status_page, name='status_page'),
    path('status/<int:service_id>/', views.service_detail, name='service_detail'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    # ServiceCheck CRUD URLs
    path('servicechecks/', views.ServiceCheckListView.as_view(), name='servicecheck_list'),
    path('servicechecks/new/', views.ServiceCheckCreateView.as_view(), name='servicecheck_create'),
    path('servicechecks/<int:pk>/', views.ServiceCheckDetailView.as_view(), name='servicecheck_detail'),
    path('servicechecks/<int:pk>/edit/', views.ServiceCheckUpdateView.as_view(), name='servicecheck_update'),
    path('servicechecks/<int:pk>/delete/', views.ServiceCheckDeleteView.as_view(), name='servicecheck_delete'),

    # Alert CRUD URLs
    path('alerts/', views.AlertListView.as_view(), name='alert_list'),
    path('alerts/new/', views.AlertCreateView.as_view(), name='alert_create'),
    path('alerts/<int:pk>/', views.AlertDetailView.as_view(), name='alert_detail'),
    path('alerts/<int:pk>/edit/', views.AlertUpdateView.as_view(), name='alert_update'),
    path('alerts/<int:pk>/delete/', views.AlertDeleteView.as_view(), name='alert_delete'),

    # MaintenanceWindow CRUD URLs
    path('maintenancewindows/', views.MaintenanceWindowListView.as_view(), name='maintenancewindow_list'),
    path('maintenancewindows/new/', views.MaintenanceWindowCreateView.as_view(), name='maintenancewindow_create'),
    path('maintenancewindows/<int:pk>/', views.MaintenanceWindowDetailView.as_view(), name='maintenancewindow_detail'),
    path('maintenancewindows/<int:pk>/edit/', views.MaintenanceWindowUpdateView.as_view(), name='maintenancewindow_update'),
    path('maintenancewindows/<int:pk>/delete/', views.MaintenanceWindowDeleteView.as_view(), name='maintenancewindow_delete'),

    path('api/', include(router.urls)), # Include API URLs
]