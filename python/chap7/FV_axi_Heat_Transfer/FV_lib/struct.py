class Struct(object):
    def __init__(self, *args, **kwargs):
        """
        Initialise l'objet Struct de plusieurs façons possibles.
        Si aucun argument n'est passé, crée un objet vide.
        """
        # Traiter les arguments positionnels (dictionnaires)
        for arg in args:
            if isinstance(arg, dict):
                for key, value in arg.items():
                    setattr(self, key, value)
        
        # Traiter les arguments nommés
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def update(self, *args, **kwargs):
        """Met à jour l'objet avec de nouveaux attributs."""
        for arg in args:
            if isinstance(arg, dict):
                for key, value in arg.items():
                    setattr(self, key, value)
        
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        return self
        
    def __repr__(self):
        attributes = vars(self)
        repr_str = ', '.join(f"{key}={value} " for key, value in attributes.items())
        return f"{self.__class__.__name__}({repr_str})"
    
if __name__ == "__main__":
    s = Struct()
    s.x=10
    print(s.x)
    s = Struct(x=1, y=2)
    print(s)
    s.update(y=20)
    print(s)