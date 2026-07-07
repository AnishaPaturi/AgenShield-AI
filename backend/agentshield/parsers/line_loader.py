import yaml

class SafeLineLoader(yaml.SafeLoader):
    """
    Custom PyYAML loader that adds __start_line__ and __end_line__ 
    information to all loaded dictionary mappings.
    """
    def construct_mapping(self, node, deep=False):
        mapping = super().construct_mapping(node, deep=deep)
        mapping['__start_line__'] = node.start_mark.line + 1
        mapping['__end_line__'] = node.end_mark.line + 1
        return mapping
