#!/usr/bin/env python3
"""
 [The "BSD license"]
  Copyright (c) 2011 Terence Parr
  All rights reserved.

  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions
  are met:
  1. Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.
  3. The name of the author may not be used to endorse or promote products
     derived from this software without specific prior written permission.

  THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
  IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
  OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
  NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
  THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
from typing import Any, Dict

from org.stringtemplate.v4.interpreter import Interpreter
from org.stringtemplate.v4.model_adaptor import ModelAdaptor
from org.stringtemplate.v4.st import ST
from org.stringtemplate.v4.misc.aggregate import Aggregate
from org.stringtemplate.v4.misc.map_model_adaptor import (
    MapModelAdaptor,
)  # Assuming this exists
from org.stringtemplate.v4.misc.st_no_such_property_exception import (
    STNoSuchPropertyException,
)


class AggregateModelAdaptor(ModelAdaptor[Aggregate]):
    """
    Deals with structs created via ST.addAggr("structname.{prop1, prop2}", ...).
    """

    def __init__(self):
        self.map_adaptor = MapModelAdaptor()

    def get_property(
        self,
        interp: Interpreter,
        st: ST,
        o: Aggregate,
        property: Any,
        property_name: str,
    ) -> Any:
        """
        Retrieves a property from the Aggregate object.  Delegates to
        MapModelAdaptor since Aggregate internally uses a dictionary.

        Args:
            interp: The interpreter instance.
            st: The ST instance.
            o: The Aggregate instance.
            property:  The property object (often the same as property_name).
            property_name: The name of the property.

        Returns:
            The value of the property.

        Raises:
            STNoSuchPropertyException: If the property does not exist.
        """
        return self.map_adaptor.get_property(
            interp, st, o.properties, property, property_name
        )


"""
Key changes and explanations:

    Inheritance: AggregateModelAdaptor now inherits from ModelAdaptor[Aggregate]. The ModelAdaptor class is assumed to be a generic class (or a type-hinted base class), similar to Java's generics. This provides type safety.
    map_adaptor: An instance of MapModelAdaptor is created in the constructor, as in the Java code. This is used to delegate the actual property retrieval, since Aggregate uses a dictionary internally.
    get_property(): This method implements the core logic. It directly delegates to the map_adaptor's get_property method, passing the Aggregate object's internal properties dictionary. This correctly handles the case where the property is not found, as the MapModelAdaptor will raise the appropriate STNoSuchPropertyException.
    Type Hints: Type hints are used extensively for improved code clarity and maintainability.
    Imports: All necessary imports have been included.

This Python class effectively replicates the functionality of the Java AggregateModelAdaptor. It provides a way for StringTemplate to access properties of Aggregate objects by treating them like dictionaries (or Maps in Java), leveraging the existing MapModelAdaptor. The use of generics/type hints in the inheritance from ModelAdaptor adds a layer of type safety.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
