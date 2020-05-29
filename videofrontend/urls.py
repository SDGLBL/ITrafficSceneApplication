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
             path('imageofvideo', views.get_image_of_video_view, name='image_of_video'),
             # 返回历史任务记录
             path('tasklist', views.get_task_list, name='task_list'),
             # 根据车牌号和任务名返回违规信息
             path('violationinfo', views.get_vehicle_violation_by_number_plate, name='violation_info'),
             # 根据任务名，起始时间，结束时间，查询违规历史折线图信息
             path('historylinechart', views.get_history_traffic_volume_line_chart, name='history_line_chart'),
             # 实时获取车流量信息表
             path('passcounttable', views.get_pass_count_table_statistics, name='pass_count_table'),
             # 获取实时车辆信息(pass)
             path('realtimevehicleinfo', views.get_real_time_vehicle_statistics, name='real_time_vehicle_info')
             ]