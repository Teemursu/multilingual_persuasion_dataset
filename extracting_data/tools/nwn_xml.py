def get_nwn_ids():
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
            except TypeError:
                return None

            # TODO: CHECK IF ANY MISSING DATA
            try:
                entry_keys = entry.keys()
            except AttributeError:
                return None
            for key in entry_keys:
                if key == "locstring":
                    string_id = entry["locstring"]["@strref"]
                    if string_id == "4294967295":
                        string_id = "EoC"
                try:
                    # df.at[entry_id, 'id'] = entry_id
                    df.at[entry_id, "sid"] = string_id
                    df.at[entry_id, "filename"] = file
                    df.at[entry_id, "game"] = "NWN 1"
                    id_sid_mapping[entry_id] = string_id
                except UnboundLocalError:
                    pass

    def update_speakers(xml_dict, list_type):
        for entry in entry_dict:
            try:
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
                                if entry["list"]["@label"] == "RepliesList":
                                    entry_id = entry["@id"] + "_entry"
                                    reply_id = (
                                        entry["list"]["struct"]["uint32"]["#text"]
                                        + "_reply"
                                    )
                                    df.at[entry_id, "replies"] = [
                                        id_sid_mapping[reply_id]
                                    ]
                                if entry["list"]["@label"] == "EntriesList":
                                    entry_id = entry["@id"] + "_reply"
                                    reply_id = (
                                        entry["list"]["struct"]["uint32"]["#text"]
                                        + "_entry"
                                    )
                                    df.at[entry_id, "replies"] = [
                                        id_sid_mapping[reply_id]
                                    ]
                            except KeyError:
                                pass
                        except TypeError:
                            replies = []
                            try:
                                if entry["list"]["@label"] == "EntriesList":
                                    for reply in entry["list"]["struct"]:
                                        entry_id = entry["@id"] + "_reply"
                                        reply_id = reply["uint32"]["#text"] + "_entry"
                                        replies.append(id_sid_mapping[reply_id])
                                        df.at[entry_id, "replies"] = replies
                                if entry["list"]["@label"] == "RepliesList":
                                    try:
                                        for reply in entry["list"]["struct"]:
                                            entry_id = entry["@id"] + "_entry"
                                            reply_id = (
                                                reply["uint32"]["#text"] + "_reply"
                                            )
                                            replies.append(id_sid_mapping[reply_id])
                                            df.at[entry_id, "replies"] = replies
                                    except KeyError:
                                        pass
                            except TypeError:
                                pass

    # kotor1_files = getListOfFiles('infinity_engine/kotor1/xml/')
    # kotor2_files = getListOfFiles('infinity_engine/kotor2/xml/')
    nwn_files = getListOfFiles("extracting_data/infinity_engine/nwn/xml/")
    # files = kotor1_files + kotor2_files + nwn_files
    files = nwn_files
    # files = [list(files)[4]]
    for file in files:
        df = pd.DataFrame(columns=["filename", "id", "sid"])
        with open(file, "rb") as f:
            xml = xmltodict.parse(f)
            xml = json.dumps(xml)
            xml = json.loads(xml)
            xml_dict = xml["gff3"]["struct"]["list"]
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
                            update_idx(entry_dict, list_type, file)
                        except KeyError:
                            # print("Error finding struct for", elem)
                            pass
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
                            # print("Error finding struct for", elem)
                            pass
                        # update_speakers(entry_dict, list_type)
                        # update_replies(entry_dict, list_type)
                except TypeError:
                    pass

        # df['replies'] = [ [] if x is np.NaN else x for x in df['replies'] ]
        # df['speaker'] = df['speaker'].fillna("PC")
        df = df[df.sid != "EoC"]
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        # print(df.to_string(index=False))
        # data = [df['sid'], df['speaker'],df['replies']]
        # headers = ['sid', 'speaker', 'replies']
        # df = pd.concat(data, axis=1, keys=headers, ignore_index=True)
        with pd.option_context(
            "display.max_rows", None, "display.max_columns", None
        ):  # more options can be specified also
            pass
        dfs.append(df)

    df = [df.set_index("sid") for df in dfs]
    df = pd.concat(df, axis=0)

    filename = "data/ids/nwn_dataset.csv"
    df.to_csv(filename, encoding="utf-8")
