def save_transcription_markdown(transcriptions, output_file):
    md_content = "# Transcrição\n\n"
    for idx, transcription in enumerate(transcriptions):
        md_content += f"## Parte {idx+1}\n\n{transcription}\n\n"
    
    with open(output_file, "w") as md_file:
        md_file.write(md_content)
