# cython: language_level=2
#!/usr/bin/env python
#distutils: language = c++

from libcpp.map cimport map
from libcpp.string cimport string

cdef class Components:
   cdef map[string, double] _list
   cpdef Components copy(Components)
   cpdef Components mix(Components, Components)
   cpdef double totalMass(Components)
   cpdef double avgMolarMass(Components)
   cpdef Components elementalComposition(Components)
   cpdef Components scale(Components, double)
   cpdef double total(Components)
   cpdef Components normalised(Components)
   cpdef list values(Components)
   cpdef list keys(Components)
   cpdef list iteritems(Components)
