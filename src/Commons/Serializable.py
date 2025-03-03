from typing import Any, Optional
import json
import logging as log
from dataclasses import field, fields
import os

from src.Commons.FileManagement import FileManagement

class Serializable(FileManagement):
    """
    Abstract class for classes that have to be serializable. Includes methods for working with
    text JSONs, as well as some extra comodity methods for excluding private elements from 
    those JSON strings, passing a reference to the possible outer class of an inner one, and a
    config dialog (most of the abstract methods comming empty)
    """
    _outer: Any = field(default=None)

    def exclude_private(self) -> dict:
        """
        Excludes private properties from dictionary for JSON serialization

        :return: (dict) Filtered dictionary
        """
        no_private: dict = self.__dict__.copy()
        keys_to_pop = list([key for key, val in self.__dict__.items() if key[0] == "_"])
        for key in keys_to_pop:
            no_private.pop(key)
        return no_private

    @classmethod    # FIXME: should be private but have to fix class parity in InspectionLibEfi first
    def from_dict(cls, self: Any) -> Optional[object]:
        """
        Helper class for deserializing JSONs

        Args:
            self (Any): Any type object, used to help deserialization
        
        Returns:
            object: Object of current class with info from json string
        """
        
        field_types = {f.name: f.type for f in fields(cls)}
        kwargs = {}
        for field_name, field_type in field_types.items():
            value = self.get(field_name)
            if value is not None:
                if type(value) is dict:
                    kwargs[field_name] = field_type.from_dict(value)
                else:
                    kwargs[field_name] = field_type(value)
            else:
                kwargs[field_name] = field_type()
        return cls(**kwargs)
        
    @classmethod
    def deserialize(cls, json_string: str) -> object:
        """
        Deserializes JSON string to object according to the cls.from_dict method

        Args:
            json_string (str): Serialized object
        
        Returns:
            object: Object from json
        """

        _obj: type(cls) = cls.from_dict(json.loads(json_string)) # type: ignore
        return _obj

    def serialize(self) -> str:
        """
        Serializes object in a JSON format (excluding private parameters)

        Returns:
            str: Serialized object
        """
        return json.dumps(self, default=lambda o: o.exclude_private(), sort_keys=False, indent=4)

    @classmethod
    def from_file(cls, json_file_path: str):
        """
        Gets JSON from file, and deserializes it to current object class
        
        Args:
            json_file_path (str): Res to JSON file
        
        Returns:
            (object): Deserialized from JSON
        """
        try:
            with open(cls.path_to_python(json_file_path)) as file:
                json_string = file.read()
        except Exception as ex:
            log.error(f"Couldn't open or read '{json_file_path}' ({ex}). Aborted")
            return None

        if json_string is None:
            log.error("Text from file is None. Aborted")
            return None

        json_obj = None

        try:
            json_obj = cls.deserialize(json_string)
        except Exception as ex:
            log.warning(f"Failed getting object from '{json_file_path}' ({ex})")

        if json_obj is None:
            log.error("Unable to deserialize json (is none)")
            return None

        log.info("Deserialized object correctly")
        return json_obj

    @classmethod
    def to_recursive_list(cls):
        field_types = {f.name: f.type for f in fields(cls)}
        kwargs = {}
        
        md_lst = []
        
        for item_name, item_type in field_types.items():
            if item_name[0] != "_":
                item_type_full = str(item_type)
                item_type_name = item_type.__name__
                
                md_lst.append(f"- `({item_type_name}) {item_name}`: >> Description")
                
                if "." in item_type_full[1:-1]:
                    inners = item_type.to_recursive_list()
                    for inner in inners:
                        md_lst.append(f"\t{inner}")
        
        return md_lst
    
    @classmethod
    def to_documentation_template(cls, out_path: str):
        md_txt = DOCUMENTATION_TEMPLATE.replace("[CLASS_NAME]", cls.__name__)
        md_txt = md_txt.replace("[FIELDS]", "\n".join(cls.to_recursive_list()))
        md_txt = md_txt.replace("[DEFAULT_JSON]", cls().serialize())
        
        with open(out_path, "w") as file:
            file.write(md_txt)
            file.close()
            
        return
    
    def to_file(self, file_path: str):
        """
        Saves an object onto a specified file

        :param file_path: (str) Res to file where to save the object, serialized as json
        :return: (str) Returns file_path back
        """

        file_path = self.path_to_python(file_path)

        # check if a file extension was specified
        if "." not in file_path:
            log.warning("The path specified has no file extension. File not saved")
            return None

        # check if path to dir existed
        dir_path = file_path[:file_path.rfind("/")]

        if not os.path.exists(dir_path):
            log.info(f"Dir didn't exist. Created '{dir_path}'")
            os.mkdir(dir_path)

        with open(file_path, "w") as file:
            file.write(self.serialize())
            log.info("Object successfully saved on file")

        return file_path

    @classmethod
    def config_dialog(cls):
        """
        Launches a configuration dialog that asks for user input for each parameter from the class. Returns an object
        """

        log.error("This class does not implement this method")
        pass

    def pass_outer(self, outer):
        """
        Passes outer object to inner, and stores it inside the private property 'cls._outer'

        Args:
            outer (object): Outer object
        """

        self._outer = outer
