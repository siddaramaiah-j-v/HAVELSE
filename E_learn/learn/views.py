import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
import urllib.parse
from .models import Course
from django.utils.text import slugify
from django.core.paginator import Paginator
from django.http import JsonResponse
import re,json,markdown,bleach


MAX=50
URL="https://www.googleapis.com/youtube/v3/search"

@login_required
def home(request):
    return render(request,'learn/home.html')

@login_required
def topics(request):
    courses=Course.objects.all()
    return render(request,'learn/topic.html',{'courses':courses})

@login_required
def article(request):
    slug=request.GET.get('slug')
    course=Course.objects.get(slug=slug)
    content=course.sections.all()
    for section in content:
        section.content=processed(section.content)
        section.slug=slugify(section.title)
    return render(request,'learn/article.html',{'sections':content,'course':course})

@login_required
def video(request):
    slug=request.GET.get('slug')
    l_name=request.GET.get('l_name','English')
    course=Course.objects.get(slug=slug)
    languages=course.languages.all()
    playlist={}
    for item in languages:
        if item.language==l_name:
            playlist=item.playlists.all()
    return render(request,'learn/videos.html',{'languages':languages,'playlist':playlist,'course':course})

@login_required
def search(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        query = urllib.parse.quote(query)
        request.session.pop('context',None)
        context = []
        params={
            'part':'snippet',
            'maxResults':MAX,
            'q':query,
            'key':settings.YOUTUBE_KEY,
            'type':'video',
            'videoEmbeddable':'true',
            'videoDuration':'long',
        }
        try:
            response = requests.get(URL,params=params)
            response.raise_for_status()
            data = response.json().get('items')
        except requests.exceptions.RequestException as e:
            data = {}
        for item in data:
            id_info = item['id']
            snippet = item['snippet']
            context.append({
                'id': id_info['videoId'],
                'title': snippet['title'],
                'description': snippet['description'],
            })
        request.session['context']=context
        paginator=Paginator(context,6)
        data=paginator.get_page(1)
        return render(request, 'learn/search.html', {'data': data})
    else:
        context = request.session.get('context')
        paginator = Paginator(context, 6)
        page_num=request.GET.get('page',1)
        data = paginator.get_page(page_num)
        return render(request, 'learn/search.html', {'data': data})


'''this section for handling the gemini responses'''

SAMPLE_RESPONSES = {
    'python': "Python is a versatile programming language. Here's a simple example:\n\n```python\ndef greet(name):\n    return f\"Hello, {name}!\"\n\nprint(greet(\"World\"))\n```\n\nWould you like to learn more about Python functions?",
    'javascript': "JavaScript is great for web development. Here's a simple function:\n\n```javascript\nfunction greet(name) {\n    return `Hello, ${name}!`;\n}\n\nconsole.log(greet(\"World\"));\n```\n\nDo you want to know more about JavaScript functions?",
    'java': "Java is widely used for enterprise applications. Here's a simple example:\n\n```java\npublic class HelloWorld {\n    public static void main(String[] args) {\n        System.out.println(\"Hello, World!\");\n    }\n}\n```\n\nWould you like to learn more about Java classes?",
    'help': "I can help you with:\n- Programming concepts\n- Debugging code\n- Learning resources\n- Best practices\n\nWhat specific coding help do you need today?",
}


try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

if GEMINI_AVAILABLE:
    genai.configure(api_key=settings.GEMINI_KEY)


def process_code_blocks(content):
    """
    Format code blocks in the message content for proper display
    """
    # Look for code blocks with language specification
    pattern = r"```(\w+)?\n([\s\S]*?)```"

    def replacement(match):
        language = match.group(1) or ""
        code = match.group(2)
        return f'<div class="code-block"><pre data-language="{language}">{code}</pre></div>'

    processed_content = re.sub(pattern, replacement, content)
    return processed(processed_content)


def processed(content):
    html = markdown.markdown(
        content,
        extensions=[
            'markdown.extensions.fenced_code',  # Support ```code blocks
            'markdown.extensions.tables',  # Support tables
            'markdown.extensions.codehilite',  # Support syntax highlighting
            'markdown.extensions.nl2br'  # Convert newlines to <br>
        ]
    )

    # Define allowed HTML tags and attributes
    allowed_tags = [
        'p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'blockquote', 'pre', 'code', 'em',
        'strong', 'del', 'a', 'img', 'br', 'hr', 'table', 'thead',
        'tbody', 'tr', 'th', 'td'
    ]

    allowed_attributes = {
        'a': ['href', 'title', 'target', 'rel'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'code': ['class'],
        'pre': ['class'],
        'span': ['class', 'style'],  # Needed for code highlighting
        'td': ['colspan', 'rowspan', 'align'],
        'th': ['colspan', 'rowspan', 'align']
    }

    # Sanitize HTML to prevent XSS attacks
    clean_html = bleach.clean(
        html,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )
    return clean_html


@login_required
def chat(request):
    """
    Render the Gemini Assistant page
    """
    # You can pass additional context data here if needed
    context = {
        'title': 'HAVELSE - Gemini Assistant',
    }
    return render(request, 'learn/chat.html', context)


def chat_with_gemini(request):
    """
    API endpoint to handle chat messages with Gemini
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()

        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        # Save message history in the session for context if needed
        if 'chat_history' not in request.session:
            request.session['chat_history'] = []

        request.session['chat_history'].append({
            'role': 'user',
             'parts':[{'text':user_message}]
        })

        # Get response from Gemini API or use sample response for demo
        gemini_response = get_gemini_response(user_message, request.session.get('chat_history', []))

        # Add response to chat history
        request.session['chat_history'].append({
            'role': 'assistant',
            'parts':[{'text':gemini_response}]

        })
        request.session.modified = True

        # Process code blocks for proper display
        processed_response = process_code_blocks(gemini_response)

        return JsonResponse({
            'success': True,
            'message': gemini_response,
            'processed_message': processed_response
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_gemini_response(message, history=None):
    """
    Generate a response using Gemini API or sample responses
    """
    # If Gemini API is available, use it
    if GEMINI_AVAILABLE:
        try:
            # Configure the model
            model = genai.GenerativeModel("gemini-2.0-flash")

            # Format history for the chat API
            chat = model.start_chat(history=history)

            # Generate response
            response = chat.send_message(
                     {'parts':{'text':message}}
            )
            return response.text

        except Exception as e:
            print(f"Error using Gemini API: {str(e)}")

    # If API is not available or there was an error, use sample responses
    message_lower = message.lower()

    # Check for keywords in the message and return appropriate response
    for keyword, response in SAMPLE_RESPONSES.items():
        if keyword in message_lower:
            return response

    # Default response if no keywords match
    return "I'm here to help with your coding questions. Could you provide more details about what you'd like to learn or what problem you're trying to solve?"

@login_required
def code(request):
    return render(request,'learn/code.html')

