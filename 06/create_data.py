#!/usr/bin/env python3
from faker import Faker
import random

fake = Faker()

for i in range(12):
    with open(f'data_{i:02}.txt', 'w') as f:
        for _ in range(1000):
            f.write(f'{fake.first_name()};{fake.last_name()};{random.uniform(900, 2400):.2f}\n')