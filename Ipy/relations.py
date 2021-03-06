from autumn.Ipy.query import Query
from autumn.Ipy.model import cache

class Relation(object):
    
    def __init__(self, model, field=None):
        self.model = model
        self.field = field
    
    def _set_up(self, instance, owner):
        if isinstance(self.model, basestring):
            self.model = cache.get(self.model)

class ForeignKey(Relation):
        
    def __get__(self, instance, owner):
        super(ForeignKey, self)._set_up(instance, owner)
        if not instance:
            return self.model
        if not self.field:
            self.field = '%s_id' % self.model.tablename()
            
        conditions = {self.model.Meta.pk: getattr(instance, self.field)}
        return Query(model=self.model, **conditions)[0]

class OneToMany(Relation):
    
    def __get__(self, instance, owner):
        super(OneToMany, self)._set_up(instance, owner)
        if not instance:
            return self.model
        if not self.field:
            self.field = '%s_id' % instance.tablename()
        conditions = {self.field: getattr(instance, instance.Meta.pk)}
        return Query(model=self.model, **conditions)
    
class JoinBy(Relation):
    '''
    Like ForiegnKey but drops requirement to join by primary key,
    and allows for expansion of join criteria.
    Should be used much less frequently than ForeignKey, since it
    is probably not as efficient.
    '''
    def __init__(self, model, field=None, joinby=None, **kwargs):
        Relation.__init__(self, model, field)
        if joinby:
            self.joinby = joinby
        else:
            self.joinby = field
        self.otherconditions = {}
        for k in kwargs:
            self.otherconditions.update({k: kwargs[k]})
            
        
    def __get__(self, instance, owner):
        super(JoinBy, self)._set_up(instance, owner)
        if not instance:
            return self.model
        if not self.field:
            self.field = '%s_id' % instance.tablename()
        conditions = {self.field: getattr(instance, self.joinby)}
        for qry in self.otherconditions:
            conditions.update({qry: getattr(instance, self.otherconditions[qry])})
        return Query(model=self.model, **conditions)
