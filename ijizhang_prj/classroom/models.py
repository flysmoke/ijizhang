from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


# Create your models here.
class BaseModel(models.Model):
    create_time         = models.DateTimeField(auto_now_add=True)
    create_by_user      = models.ForeignKey(User, related_name="+")
    class Meta:
        abstract = True
        
        
class Room(BaseModel):
    name                = models.CharField(max_length=200)
    draw_by_user        = models.ForeignKey(User, related_name="author")
    members             = models.ManyToManyField(User, related_name='join_rooms')
    
    class Meta:
        db_table        = 'class_room'

    def __unicode__(self):
        return self.name 

    def get_absolute_url(self):
        return '%s' % (reverse('classroom:detail_room', args=[self.id]))      
        
    def get_add_member_url(self):
        add_type = 1
        return '%s' % (reverse('classroom:join_room', kwargs={'room_id':self.id,'add_type':add_type})) 
        
    def get_remove_member_url(self):
        add_type = 0
        return '%s' % (reverse('classroom:join_room', kwargs={'room_id':self.id,'add_type':add_type}))  
            
class Draw(BaseModel):
    name                = models.CharField(max_length=50000)    
    color           = models.CharField(max_length=40)
    room            = models.ForeignKey(Room, db_column='room', related_name="draws")
    class Meta:
        db_table        = 'class_draw'
    def __unicode__(self):
        return self.name 
class Comment(BaseModel):
    name                = models.CharField(max_length=2000)    
    room            = models.ForeignKey(Room, db_column='room', related_name="comments")
    class Meta:
        db_table        = 'class_comment'  

    def __unicode__(self):
        return self.name       