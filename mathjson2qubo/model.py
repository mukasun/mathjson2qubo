import numbers
import re

import numpy as np


class Model:
    @classmethod
    def make_model_from_tuple(cls, obj):
        label_set, quadratic, const = cls._make_label_quadratic_from_tuple(obj)
        matrix, label_sorted = cls._make_mat_from_l_quad(label_set, quadratic)
        return matrix, const, label_sorted

    @classmethod
    def _make_label_quadratic_from_dict(cls, obj):
        label_set = set()
        quadratic = {}
        for key, value in obj.items():
            if isinstance(key, tuple):
                label_set |= set(key)
                quadratic[key] = value

            elif isinstance(key, str):
                label_set.add(key)
                quadratic[(key, key)] = value

        return label_set, quadratic

    @classmethod
    def _make_label_quadratic_from_tuple(cls, obj):
        label_set = set()
        quadratic = {}
        const = 0
        for value in obj:
            if isinstance(value, dict):
                lab_set, qua = cls._make_label_quadratic_from_dict(value)
                quadratic.update(qua)
                label_set |= lab_set
            elif isinstance(value, (numbers.Real, np.number)):
                const += value
            else:
                raise TypeError("Object is TypeError.")
        return label_set, quadratic, const

    @classmethod
    def _make_mat_from_l_quad(cls, label_set, quadratic):
        label = cls._make_new_label2index_sorted(label_set)
        spins = len(label)
        matrix = np.zeros((spins, spins))
        for k, v in quadratic.items():
            x = label[str(k[0])]
            y = label[str(k[1])]
            matrix[x, y] = v
            matrix[y, x] = v
        return matrix, label

    @classmethod
    def _make_new_label2index_sorted(cls, label_sequence):
        label_sorted = cls._sort_label(label_sequence)
        return {key: num for num, key in enumerate(label_sorted)}

    @classmethod
    def _sort_label(cls, label_sequence):
        structure = cls._make_stracture(label_sequence)
        label_sorted = sorted(structure.items(), key=lambda x: x[1])
        return [item[0] for item in label_sorted]

    @classmethod
    def _make_stracture(cls, label_sequence):
        structure = {}
        for label in label_sequence:
            result = re.findall(r"\w+", label)
            structure[label] = tuple(int(c) if c.isdigit() else c for c in result)
        return structure
