import spacy


class SpacyHelper:
    @staticmethod
    def get_time_text(raw: str):
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(raw)
        print(doc)
        for ent in doc.ents:
            print(ent.text, ent.start_char, ent.end_char, ent.label_)
            if ent.label_ == 'TIME':
                time = ent.text
                print("label: TIME")
                print(time)
                return str(time)
            elif ent.label_ == "CARDINAL":
                time = ent.text
                print("label: CARDINAL")
                print(time)
                return time

    @staticmethod
    def get_date_text(raw: str):
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(raw)
        print(doc)
        for ent in doc.ents:
            print(ent.text, ent.start_char, ent.end_char, ent.label_)
            if ent.label_ == 'DATE':
                return True, ent.text
            else:
                return False, 'None'