from django.db import models
from django.contrib.auth.models import User

class Rooms_01(models.Model):
    name=models.CharField(max_length=100, unique=True,verbose_name='nombre')
    users= models.ManyToManyField(User,related_name='rooms_joined',blank=True)
    
    def __str__(self):
        return self.name
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'users': [user.username for user in self.users.all()], # Convierte el ManyRelatedManager a una lista de IDs
            # Agrega aquí cualquier otro campo que quieras incluir en la serialización
        }