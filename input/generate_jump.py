#!/usr/bin/env python3
from math import ceil, floor

n_values = [10, 20, 50, 100, 200, 500]
for n in n_values:
	m_values = [2, ceil(n/8), ceil(n/4), ceil(3*n/8),floor(n/2)]
	for m in m_values:
		print(str(m) + '_' + str(n), m, n)
