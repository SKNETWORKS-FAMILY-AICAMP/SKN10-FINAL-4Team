def generate_voiceid(youtube_url):
    # Your logic to generate a voice ID from YouTube
    return "voiceid_from_youtube"

def generate_feature_model_id(youtube_url, speech=False):
    # Your logic to generate a model ID
    return "modelid_from_youtube" if not speech else "speech_modelid_from_youtube"

def generate_prompts(youtube_url, prompt_type='feature'):
    # Your logic to generate prompts
    return f"{prompt_type}_prompt_based_on_youtube"