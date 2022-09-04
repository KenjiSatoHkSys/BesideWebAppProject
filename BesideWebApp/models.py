from django.db import models


class Beside_db(models.Model):
    no = models.IntegerField()  # serial number of beside set by user for display on table
    room_name = models.CharField(max_length=110)   # component of API url
    disp_name = models.CharField(max_length=100)   # name of measuring location for displaying on table
    co2_calib = models.FloatField()  # modification value for adding measured co2 value to get actual value
    map_x = models.FloatField()
    map_y = models.FloatField()

    def __str__(self):
        return 'id:'+str(self.id)+', no:'+str(self.no)+', room_name:'+self.room_name+', disp_name:'+self.disp_name+\
               ', co2_calib:'+str(self.co2_calib)+', map_x: '+str(self.map_x)+', map_y: '+str(self.map_y)

class Openweather_db(models.Model):
    api_key = models.CharField(max_length=100)
    location = models.CharField(max_length=100)  # eg. OSAKA
    url_init = models.CharField(max_length=200)  # url for retrieving longitude and latitude of measuring location
    url_meas = models.CharField(max_length=200)  # url for retrieve data

    def __str__(self):
        return 'id:'+str(self.id)+', api_key:'+self.api_key+', location: '+self.location+\
               ', url_init: '+self.url_init+', url_meas: '+self.url_meas

class Manager_db(models.Model):
    # データ取得サイクル。OpenWeatherアクセス頻度：無償版はAPIの呼び出しが100万コール/月（60コール/分）以内
    cycle = models.IntegerField()  # data retrieving cycle (second)

    def __str__(self):
        return 'id:'+str(self.id)+', cycle: '+str(self.cycle)