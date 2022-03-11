def get_kotor1_ids():
    import xml.etree.ElementTree as ET
    import os
    import xmltodict, json, xmljson
    from pprint import pprint
    import pandas as pd
    import ast
    import re
    import numpy as np

    dfs = []
    id_sid_mapping = {}

    def getListOfFiles(dirName):
        # create a list of file and sub directories
        # names in the given directory
        listOfFile = os.listdir(dirName)
        allFiles = list()
        # Iterate over all the entries
        for entry in listOfFile:
            # Create full path
            fullPath = os.path.join(dirName, entry)
            # If entry is a directory then get the list of files in this directory
            if os.path.isdir(fullPath):
                allFiles = allFiles + getListOfFiles(fullPath)
            else:
                allFiles.append(fullPath)

        return allFiles

    def update_idx(xml_dict, list_type, file):
        for entry in xml_dict:
            # TODO:
            try:
                if list_type == "EntryList":
                    entry_id = entry["@id"] + "_entry"
                if list_type == "ReplyList":
                    entry_id = entry["@id"] + "_reply"
                if list_type == "StartingList":
                    entry_id = entry["@id"] + "_start"
            except TypeError:
                return None

            # TODO: CHECK IF ANY MISSING DATA
            try:
                entry_keys = entry.keys()
            except AttributeError:
                return None
            # if list_type == 'StartingList':
            # print(xml_dict)
            # print()
            for key in entry_keys:
                if key == "locstring":
                    string_id = entry["locstring"]["@strref"]

                    if string_id == "4294967295":
                        string_id = "EoC"
                try:

                    df.at[entry_id, "id"] = entry_id
                    df.at[entry_id, "sid"] = string_id
                    df.at[entry_id, "filename"] = file
                    if "infinity_engine/kotor1/xml/" in file:
                        df.at[entry_id, "game"] = "KotOR 1"
                    if "infinity_engine/kotor2/xml/" in file:
                        df.at[entry_id, "game"] = "KotOR 2"
                    id_sid_mapping[entry_id] = string_id
                except UnboundLocalError:
                    pass

    def update_speakers(xml_dict, list_type):
        for entry in entry_dict:
            try:

                if list_type == "StartingList":
                    entry_id = entry["@id"] + "_start"
                else:
                    entry_id = entry["@id"] + "_entry"
            except TypeError:
                return None

            for key in entry.keys():
                if key == "exostring":
                    for elem in entry["exostring"]:

                        try:
                            if elem["@label"] == "Speaker":
                                df.at[entry_id, "speaker"] = elem["#text"]

                        except KeyError:
                            df.at[entry_id, "speaker"] = "not_found"

    def update_replies(xml_dict, list_type):
        for entry in xml_dict:
            try:
                entry_keys = entry.keys()
            except AttributeError:
                return None

            for key in entry_keys:
                if key == "list":
                    for elem in entry["list"]:

                        try:
                            try:

                                if elem["@label"] == "RepliesList":
                                    entry_id = entry["@id"] + "_entry"

                                    reply_id = (
                                        elem["struct"]["uint32"]["#text"] + "_reply"
                                    )
                                    df.at[entry_id, "replies"] = [
                                        id_sid_mapping[reply_id]
                                    ]
                                if elem["@label"] == "EntriesList":
                                    entry_id = entry["@id"] + "_reply"
                                    reply_id = (
                                        elem["struct"]["uint32"]["#text"] + "_entry"
                                    )
                                    df.at[entry_id, "replies"] = [
                                        id_sid_mapping[reply_id]
                                    ]

                            except KeyError:
                                pass
                        except TypeError:
                            replies = []
                            if elem["@label"] == "EntriesList":
                                for reply in elem["struct"]:
                                    entry_id = entry["@id"] + "_reply"
                                    reply_id = reply["uint32"]["#text"] + "_entry"
                                    replies.append(id_sid_mapping[reply_id])
                                    df.at[entry_id, "replies"] = replies
                            if elem["@label"] == "RepliesList":
                                try:
                                    for reply in elem["struct"]:
                                        entry_id = entry["@id"] + "_entry"
                                        reply_id = reply["uint32"]["#text"] + "_reply"
                                        replies.append(id_sid_mapping[reply_id])
                                        df.at[entry_id, "replies"] = replies
                                except KeyError:
                                    pass

    kotor1_files = getListOfFiles("extracting_data/infinity_engine/kotor1/xml/")
    kotor2_files = getListOfFiles("extracting_data/infinity_engine/kotor2/xml/")

    # nwn_files = getListOfFiles('extracting_data/infinity_engine/nwn/xml/')
    files = kotor1_files
    # files = nwn_files
    # files = [list(files)[5]]
    for file in files:
        df = pd.DataFrame(columns=["game", "filename", "id", "sid"])

        with open(file, "rb") as f:
            xml = xmltodict.parse(f)
            xml = json.dumps(xml)
            xml = json.loads(xml)
            try:
                xml_dict = xml["gff3"]["struct"]["list"]
            except KeyError:
                # print(xml)
                pass
            # print("Processing file:",file)
            for elem in xml_dict:
                try:
                    if (
                        elem["@label"] == "EntryList"
                        or elem["@label"] == "ReplyList"
                        or elem["@label"] == "StartingList"
                    ):
                        list_type = elem["@label"]
                        try:
                            entry_dict = elem["struct"]
                        except KeyError:
                            # print("Error finding struct for",elem)
                            pass
                        update_idx(entry_dict, list_type, file)
                except TypeError:
                    pass

            for elem in xml_dict:
                try:
                    if (
                        elem["@label"] == "EntryList"
                        or elem["@label"] == "ReplyList"
                        or elem["@label"] == "StartingList"
                    ):
                        list_type = elem["@label"]
                        try:
                            entry_dict = elem["struct"]
                        except KeyError:
                            # print("Error finding struct for",elem)
                            pass

                        # update_speakers(entry_dict, list_type)
                        # update_replies(entry_dict, list_type)
                except TypeError:
                    pass

        # df["replies"] = [[] if x is np.NaN else x for x in df["replies"]]
        # df["speaker"] = df["speaker"].fillna("PC")
        df = df[df.sid != "EoC"]
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        # print(df.to_string(index=False))
        # data = [df['sid'], df['speaker'],df['replies']]
        # headers = ['sid', 'speaker', 'replies']
        # df = pd.concat(data, axis=1, keys=headers, ignore_index=True)
        dfs.append(df)

    df = [df.set_index("sid") for df in dfs]
    df = pd.concat(df, axis=0)
    filename = "data/ids/kotor1_dataset.csv"
    df.to_csv(filename, encoding="utf-8")
