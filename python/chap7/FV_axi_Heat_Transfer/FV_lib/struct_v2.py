class Struct:
    def __init__(self, *args, recursive=False, **kwargs):
        """
        Initialise un objet Struct.
        
        Args:
            *args: Dictionnaires positionnels à intégrer.
            recursive (bool): Si True, convertit récursivement les dicts en Struct.
            **kwargs: Paires clé/valeur à ajouter comme attributs.
        """
        self._reserved = set(dir(self))  # Noms réservés à ne pas écraser

        # Traiter les dictionnaires passés en args
        for arg in args:
            if not isinstance(arg, dict):
                raise TypeError(f"Argument positionnel invalide : {arg} (type {type(arg)})")
            self._set_attrs(arg, recursive)

        # Traiter les kwargs
        self._set_attrs(kwargs, recursive)

    def _set_attrs(self, d, recursive):
        for key, value in d.items():
            if key in self._reserved:
                raise AttributeError(f"Le nom '{key}' est réservé et ne peut pas être utilisé comme attribut.")
            if recursive and isinstance(value, dict):
                setattr(self, key, Struct(value, recursive=True))
            else:
                setattr(self, key, value)

    def update(self, *args, recursive=False, **kwargs):
        """
        Met à jour les attributs de l'objet.
        
        Args:
            *args: Dictionnaires positionnels.
            recursive (bool): Si True, convertit récursivement les dicts en Struct.
            **kwargs: Nouvelles paires clé/valeur.
        """
        for arg in args:
            if not isinstance(arg, dict):
                raise TypeError(f"Argument positionnel invalide : {arg} (type {type(arg)})")
            self._set_attrs(arg, recursive)

        self._set_attrs(kwargs, recursive)
        return self

    def to_dict(self):
        """Retourne un dictionnaire standard à partir des attributs."""
        result = {}
        for key, value in vars(self).items():
            if isinstance(value, Struct):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result

    def __repr__(self):
        attributes = vars(self)
        repr_str = ', '.join(f"{key}={value!r}" for key, value in attributes.items())
        return f"{self.__class__.__name__}({repr_str})"


if __name__ == "__main__":
    # Exemple d'utilisation
    s = Struct(x=1, y=2)
    print(s)

    s.update({'y': 20, 'z': 30})
    print(s)

    # Test récursif
    nested = Struct({'a': {'b': 1}}, recursive=True)
    print(nested)
    print(nested.a.b)

    # Conversion en dictionnaire
    print(nested.to_dict())
