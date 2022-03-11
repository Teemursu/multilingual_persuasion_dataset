from extracting_data.tools.nwn_xml import get_nwn_ids
from extracting_data.tools.kotor1_xml import get_kotor1_ids
from extracting_data.tools.kotor2_xml import get_kotor2_ids
from extracting_data.tools.sid_to_str import get_dialogue_from_ids
from extracting_data.tools.data_processing import process_data


if __name__ == "__main__":

    # Get the string identifiers from the game XML files (converted from .dlg)
    get_nwn_ids()
    get_kotor1_ids()
    get_kotor2_ids()

    # Get the dialogue strings based on the string ids
    get_dialogue_from_ids()

    # Clean up the strings (remove game dev commentary, tags, etc.)
    process_data()
