from django.http import JsonResponse
from spleeter.separator import Separator
from rest_framework.decorators import api_view
from openai import OpenAI
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from django.views.decorators.csrf import csrf_exempt
from pydub import AudioSegment
import speech_recognition as sr
import pysrt
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from spleeter.separator import Separator
import soundfile as sf
import tempfile
import shutil
import subprocess
from pydub import AudioSegment
from django.core.files.base import ContentFile

@api_view(['POST'])
def remove_vocals(request):
    if request.method == 'POST':
        # Assuming the audio file is uploaded as a file
        audio_file = request.FILES.get('audio_file')
        
        if audio_file:
            try:
                # Initialize Spleeter separator
                separator = Separator('spleeter:2stems')
                
                # Get the original filename
                original_filename = audio_file.name
                
                # Define the output file path
                #output_directory = '/home/macapp/Downloads/song/vocals/' #Local path for store the vocals and karoke (local only)
                output_directory = '/home/ubuntu/Music/music_output' #server folder path
                output_file_path = os.path.join(output_directory, original_filename)
                
                # Process audio file to remove vocals
                separator.separate_to_file(audio_file.temporary_file_path(), output_file_path)
                
                # Return the path to the processed audio file
                return JsonResponse({'processed_audio_path': output_file_path})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'Audio file not provided'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

     
@api_view(['POST'])
def generate_srt(request):
    #api_key = "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" ---Praveen mail id key
    #api_key = "sk-proj-JeNJFQKVsCAGKsBlyIcPT3BlbkFJLL6Pz7NfzMCLenL6jaCL" #samgiftson mail id key

    
    
    # Check if audio file is provided in the request
    if 'audio_file' not in request.FILES:
        return JsonResponse({'error': 'No audio file provided'}, status=400)
    
    # Get the file object from request.FILES
    audio_file = request.FILES['audio_file']

    filename = audio_file.name

    #audio_file_path = f'/home/macapp/Downloads/song/{filename}' #Local Path 
    audio_file_path = f'/home/ubuntu/Music/Song/{filename}' #server system
    

    # Define the file paths
  
    #subtitle_file_path = f'/home/macapp/Downloads/song/uploadsongs/{filename}.srt' #Local path
    subtitle_file_path = f'/home/ubuntu/Music/Song/uploadsongs/{filename}.srt' #server path
    


    try:
        # Save the uploaded audio file to a specific location
        with open(audio_file_path, 'wb') as destination:
            for chunk in audio_file.chunks():
                destination.write(chunk)


        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)


        # Transcribe the audio file
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="srt",
                language="ta"
            )

        # Write the transcript to the output SRT file
        with open(subtitle_file_path, 'w', encoding='utf-8') as srt_file:
            srt_file.write(transcript)

        print("SRT file saved to:", subtitle_file_path)
        
        # Return a success response
        return HttpResponse("SRT file saved successfully")

    except Exception as e:
        error_message = "An error occurred: " + str(e)
        print(error_message)
        
        # Return an error response
        return HttpResponse(error_message, status=500)




@api_view(['POST'])
def remove_vocals2(request):
    if request.method == 'POST':
        # Assuming the audio file is uploaded as a file
        audio_file = request.FILES.get('audio_file')
        
        if audio_file:
            try:
                # Initialize Spleeter separator
                separator = Separator('spleeter:2stems')
                
                # Get the original filename
                original_filename = audio_file.name
                
                # Define temporary directory for processing
                temp_dir = tempfile.mkdtemp()
                
                # Define the output file path
                output_file_path = os.path.join(temp_dir, original_filename)
                
                # Process audio file to remove vocals
                separator.separate_to_file(audio_file.temporary_file_path(), output_file_path)
                
                # Compress the audio file to reduce file size
                #compressed_output_file_path = compress_audio(output_file_path)
                output_directory = 'home/macapp/Downloads/song/vocals/'
                compressed_output_file_path = compress_audio(audio_file, output_directory)
                
                # Clean up temporary directory
                shutil.rmtree(temp_dir)
                
                # Return the path to the compressed processed audio file
                return JsonResponse({'processed_audio_path': compressed_output_file_path})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'Audio file not provided'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


def compress_audio(audio_file, output_directory):
    """
    Compresses the audio file object and saves the compressed file to the specified output directory.
    """
    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)

    # Create a temporary file to write the uploaded audio data
    with tempfile.NamedTemporaryFile(delete=False) as temp_audio_file:
        temp_audio_file_path = temp_audio_file.name
        for chunk in audio_file.chunks():
            temp_audio_file.write(chunk)

    # Generate output file path with adjusted extension if needed
    output_file_path = os.path.join(output_directory, os.path.basename(audio_file.name).replace('.wav', '_compressed.wav'))

    # Adjust compression parameters as needed
    subprocess.run(['ffmpeg', '-i', temp_audio_file_path, '-b:a', '128k', output_file_path], check=True)

    # Delete temporary file
    os.unlink(temp_audio_file_path)

    return output_file_path




@api_view(['POST'])
def merge_audio_and_karaoke(request):
    if request.method == 'POST':
        # Get the audio and karaoke file paths from the request
        audio_path = request.data.get('audio')
        karaoke_path = request.data.get('karaoke')

        if audio_path is None or karaoke_path is None:
            return JsonResponse({'error': 'Audio or karaoke file path is missing'}, status=400)

        try:
            # Load audio and karaoke files
            audio = AudioSegment.from_file(audio_path)
            karaoke = AudioSegment.from_file(karaoke_path)
        except Exception as e:
            return JsonResponse({'error': f'Error loading audio or karaoke file: {str(e)}'}, status=400)

        # Ensure the lengths of audio and karaoke are the same
        if len(audio) != len(karaoke):
            return JsonResponse({'error': 'Audio and karaoke files must be of the same length'}, status=400)

        # Mix audio and karaoke
        mixed_audio = audio.overlay(karaoke)

        # Specify the output directory and filename
        output_directory = '/home/macapp/Downloads/song/finalout' #localpath
       # output_directory = 'home/ubuntu/Music/Song/finalout' #serverpath
        output_filename = 'output_merged.mp3'
        output_path = os.path.join(output_directory, output_filename)

        # Save the mixed audio to the output file path
        mixed_audio.export(output_path, format="mp3")

        # Return the output file path
        return JsonResponse({'message': 'Merged audio and karaoke successfully!', 'output_path': output_path})

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)


