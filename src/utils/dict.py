
class DictUtils:
    @staticmethod
    def merge(dict1, dict2):
        if dict1 is None:
            return dict2
        if dict2 is None:
            return dict1
        for key in dict2:
            if key not in dict1:
                dict1[key] = dict2[key]
                continue
            dict1[key] = dict1[key] or dict2[key]

        return dict1

    @staticmethod
    def rename_key(dict, key_mapping):
        for key in key_mapping:
            dict[key_mapping[key]] = dict.pop(key)

        return dict