def get_dialogue_from_ids():
    import pandas as pd
    import xmltodict
    import json
    from pprint import pprint
    import numpy as np
    import re
    from pprint import pprint
    import ftfy

    perses = [
        "[Persu",
        ";Persu",
        "berreden]",
        "berreden&" "[Überre",
        ";Überreden",
        "[ Überre",
        "[Peru",
        ";Peru",
        "[ Persu",
        "[ Peru",
        "[Überreden/Lügen]",
        "[Überreden/Bluff]",
        # "[Insight]",
        # "[Intimidate]",
        # "[Perform]",
        # "[Bluff]",
        # "[Spellcraft]",
        # "[Lore]",
        # "[Dexterity]",
        # "[Make an Intelligence Check]",
        # "[Use Intelligence]",
        # "[Use Open Lock Skill]",
        # "[Wisdom]",
        # "[Force Persuade]",
        # "[Computer Skill]",
        # "[Repair]",
        # "[Awareness]",
        # "[Security]",
        # "[Computer]",
        # "[Demolitions]",
        # "[Treat Injury]",
        # "[Strength]",
        # "[Dexterity]",
        # "[Intelligence]",
        # "[Wisdom]",
        # "[Constitution]",
    ]

    kotor1_df = pd.read_csv("data/ids/kotor1_dataset.csv")
    kotor2_df = pd.read_csv("data/ids/kotor2_dataset.csv")
    nwn_df = pd.read_csv("data/ids/nwn_dataset.csv")
    langs = ["en", "de", "fr", "it", "es"]

    df_games_dict = {"kotor1": kotor1_df, "kotor2": kotor2_df, "nwn": nwn_df}
    for game, df in zip(df_games_dict.keys(), df_games_dict.values()):
        df["is_persuasion"] = np.nan
        df["sid"] = pd.to_numeric(df["sid"], downcast="integer")
        df.set_index("sid", inplace=True)
        for lang in langs:
            file = "extracting_data/infinity_engine/{}/tlk/{}_{}.xml".format(
                game, game, lang
            )
            print("Extracting", lang, "strings from", game)
            df[lang] = np.nan
            file = re.sub("lang", lang, file)
            with open(file, "rb") as f:
                xmlResponse = ftfy.fix_text(
                    f.read().decode("utf-8"),
                    fix_entities=False,
                    uncurl_quotes=False,
                    fix_latin_ligatures=False,
                ).encode("utf-8")
                xml = xmltodict.parse(xmlResponse)
                xml = json.dumps(xml)
                xml = json.loads(xml)
                for elem in xml["tlk"]["string"]:
                    # print(df['sid'][253])
                    try:

                        df.loc[df.index == np.intc(elem["@id"]), lang] = elem["#text"]
                        if (
                            any(map(elem["#text"].__contains__, perses))
                            and lang == "en"
                        ):
                            split_pers = elem["#text"].split("]")
                            pers_tag = re.sub("\[", "", split_pers[0])
                            pers_tag = re.sub("<StartCheck>", "", pers_tag)
                            pers_tag = re.sub("</Start>", "", pers_tag)
                            pers_tag = re.sub(" ", "", pers_tag)
                            pers_tag = re.sub(r"[\/\,\-\+]", "/", pers_tag)

                            df.loc[
                                df.index == np.intc(elem["@id"]),
                                "is_persuasion",
                            ] = pers_tag

                            """
                                    if (
                                        len(df.loc[(df.index == np.intc(elem["@id"]))]) == 0
                                        and game == "KotOR 1"
                                    ):
                                        print(elem["@id"], elem["#text"])
                                    """
                    except KeyError:
                        pass
        df_games_dict[game] = df

    df = pd.concat(
        [df for df in df_games_dict.values()],
        axis=0,
    )
    filename = "data/persuasion_dialogue_dataset.csv"
    df.to_csv(filename, encoding="utf-8")
