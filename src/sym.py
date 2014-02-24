__author__ = 'ZhangJingtian'
import errors

class IdentifierTable(object):
    """IdentifierTable class

    Chains the identifier table with different scope into a list using '_prev' filed.

    """
    def __init__(self, prev = None, owner_id = None):
        self._prev    = prev
        self._owner_id=owner_id
        self._table   = {}

    def init(self, prev, owner_id):
        self._prev = prev
        self._owner_id = owner_id

    def add(self, id_obj):
        """Add identifier to Scope

        Adds a new identfier to the current scope.

        """
        if self._table.get(str(id_obj)) is not None:
            raise errors.ParserNameError('name already declared at this scope')
        self._table[str(id_obj)] = id_obj

    def find(self, name):
        """Find Identifier in Scope

        Searches for the given identifier in the chained scope.

        Raises:
            ParserNameError if the given identifier is not found in any valid scope.

        """
        id_obj = self.lookup(name)
        if id_obj is None:
            raise errors.ParserNameError()
        return id_obj

    def lookup(self, name):
        """Look up Identifier in Scope

        Searches for the given identifier in the chained scope.

        """
        tab = self
        while tab is not None:
            id_obj = tab._table.get(name)
            if id_obj is not None:
                return id_obj
            tab = tab._prev
        return None

    def get_id_objs(self):
        return self._table.values()

    def push_scope(self):
        """Push New Identifier Scope

        Creates a new scope on the identifiers table.

        """
        id_table = IdentifierTable(self, self._owner_id)
        return id_table

    def pop_scope(self):
        """Pop Highest Identifier Scope

        Disposes of the current scope in the identifiers table.

        """
        id_table = self._prev
        return id_table


    def get_owner_id(self):
        return self._owner_id



