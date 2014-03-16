__author__ = 'ZhangJingtian'

class StaticArea(object):
    def __init__(self):
        super(StaticArea, self).__init__()
        self.global_variables = []
        self.global_used      = 0

    def emit_global_varible(self, name, width, align):
        offset = (self.global_used + (align - 1)) & (~(align-1))
        self.global_used = offset + width
        self.global_variables.append((name, offset))
        return offset

class CodeGenerator(object):
    def __init__(self):
        super(CodeGenerator, self).__init__()
        self.staic_area = StaticArea()

    def gen_global_variable(self, id_obj):
        name = str(id_obj)
        width= id_obj.get_type().get_width()
        align= id_obj.get_type().get_align()
        return self.staic_area.emit_global_varible(name, width, align)
