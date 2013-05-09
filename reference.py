'''
Modified on 2013.05.04.

@author: Ian Bicking 
@source: https://bitbucket.org/ianb/formencode , declarative.py
@modifier: arsene
'''
class classinstancemethod(object):
    """
    Acts like a class method when called from a class, like an
    instance method when called by an instance.  The method should
    take two arguments, 'self' and 'cls'; one of these will be None
    depending on how the method was called.
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, type=None):
        return _methodwrapper(self.func, obj=obj, type=type)

class _methodwrapper(object):

    def __init__(self, func, obj, type):
        self.func = func
        self.obj = obj
        self.type = type

    def __call__(self, *args, **kw):
        assert not kw.has_key('self') and not kw.has_key('cls'), (
            "You cannot use 'self' or 'cls' arguments to a "
            "classinstancemethod")
        return self.func(*((self.obj, self.type) + args), **kw)

    def __repr__(self):
        if self.obj is None:
            return ('<bound class method %s.%s>'
                    % (self.type.__name__, self.func.func_name))
        else:
            return ('<bound method %s.%s of %r>'
                    % (self.type.__name__, self.func.func_name, self.obj))

class reference( object ):
    def __init__( self, value=None ):
        self.value = value
    @classinstancemethod
    def get( self=None, cls=None, instance=None ):
        ctx = self or cls
        if ctx is cls:
            if isinstance(instance, cls): 
                return instance.value
        else:
            return self.value
    @classinstancemethod
    def set( self=None, cls=None, instance_or_value=None, value=None ):
        ctx = self or cls
        if ctx is cls:
            if isinstance( instance_or_value, cls ):
                instance_or_value.value = value
        else:
            self.value = instance_or_value

class opposite( reference ):
    def __init__( self, value=None ):
        super( opposite, self ).__init__( bool(value) if value is not None else None )
            
    @classinstancemethod
    def set( self=None, cls=None, instance_or_value=None, value=None ):
        ctx = self or cls
        if ctx is cls:
            if isinstance( instance_or_value, cls ):
                if isinstance( value, bool ) or value is None:
                    instance_or_value.value = instance_or_value.value != value
                else:
                    raise ValueError, "Opposite value has to be boolean"
        else:
            if isinstance( instance_or_value, bool ) or instance_or_value is None:
                self.value = self.value != instance_or_value
            else:
                raise ValueError, "Opposite value has to be boolean"
            