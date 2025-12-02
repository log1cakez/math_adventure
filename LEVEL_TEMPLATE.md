# Level Template System

## Directory Structure

Create directories for each level:
```
assets/photos/LEVEL 1/
assets/photos/LEVEL 2/
assets/photos/LEVEL 3/
...
assets/photos/LEVEL 10/
```

## Level Content Structure

For each level directory, add:

### 1. Question Images
- `question1.jpg` - First question image
- `question2.jpg` - Second question image
- `question3.jpg` - Third question image
- etc.

### 2. Audio Files (Optional)
- `question1.mp3` - Audio for first question
- `question2.mp3` - Audio for second question
- `question3.mp3` - Audio for third question
- etc.

### 3. Reward Videos
Create the reward videos directory:
```
videos/REWARD/
├── CORRECT.gif    - Shows when answer is correct
├── WRONG.gif      - Shows when answer is wrong
└── stars.gif      - Shows when all answers are correct
```

### 4. Reward Audio
Create the reward audio files in the background music directory:
```
assets/audio/BACKGROUND MUSIC/
├── CORRECT.mp3    - Plays when answer is correct
├── WRONG.mp3      - Plays when answer is wrong
```

**Note**: For the perfect score (stars), the CORRECT.mp3 sound will be played.

**Note**: Pygame can load GIF files as static images. For animated GIFs, you may need additional libraries like `pygame_gif` or convert them to individual frames.

## How It Works

1. **Press 1-0 on MAP.png** → Starts corresponding level
2. **Question Display** → Shows question image with audio (if available)
3. **Answer Input** → Press 1-4 to select answer
4. **Reward System**:
   - **Correct answer** → Shows CORRECT.gif + plays CORRECT.mp3 → Advances to next question
   - **Wrong answer** → Shows WRONG.gif + plays WRONG.mp3 → Returns to the same question (must retry)
   - **Perfect score** → Shows stars.gif + plays CORRECT.mp3 → Returns to map
5. **Navigation** → ESC to go back to map, SPACE/click to continue after reward

## Customizing Correct Answers

To set the correct answers for each question, modify the `load_level_questions` method in `main.py`:

```python
# Change this line in load_level_questions method:
question_data['correct_answer'] = (i % 4) + 1

# To something like:
if level_number == 1:
    correct_answers = [1, 2, 3, 4, 1]  # Answers for level 1
    question_data['correct_answer'] = correct_answers[i] if i < len(correct_answers) else 1
```

## Example Level 1 Setup

```
assets/photos/LEVEL 1/
├── question1.jpg
├── question1.mp3
├── question2.jpg
├── question2.mp3
├── question3.jpg
└── question3.mp3
```

## Testing

1. Run the game: `python main.py`
2. Navigate to MAP.png
3. Press "1" to start Level 1
4. Test the question system with 1-4 keys
5. Check reward animations

## Notes

- Images should be in JPG, PNG, or JPEG format
- Audio files should be in MP3 format
- Reward videos should be in GIF format
- The system automatically loads all images in the level directory
- Questions are displayed in alphabetical order
