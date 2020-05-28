from django.urls import path

from . import views

app_name='videofrontend'
urlpatterns=[path('',views.index,name='index'),
             # 车流量实时数据
             path('carsvolume', views.get_traffic_volume_statistics, name='cars_volume'),
             # 折线图数据
             path('carsvolumelinechart',views.get_traffic_volume_line_chart_statistics,name='line_chart'),
             # 车辆实时违规数据
             path('vehicleviolation',views.get_vehicle_violation_statistics,name='vehicle_violation'),
             # 返回图像帧
             path('imageofvideo', views.get_image_of_video_view, name='image_of_video')
             ]