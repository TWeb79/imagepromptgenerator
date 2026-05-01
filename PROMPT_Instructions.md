# Photo Prompt Generation Instructions

## Overview
This document provides guidelines for creating high-quality photo prompts for AI image generation models (Stable Diffusion, Ollama, etc.). Effective prompts combine detailed positive descriptions with strategic negative exclusions to produce optimal results.

## What Makes a Good Photo Prompt

A good photo prompt is:
- **Specific and detailed** — Avoid vague terms; describe exactly what you want
- **Structured logically** — Build from subject to environment to technical specs
- **Technically informed** — Include camera, lighting, and quality parameters
- **Balanced** — Positive guidance + negative exclusions = better control

## Prompt Structure Template

### Positive Prompt Formula
```
[Main subject], [key features], [setting/background], [lighting], [camera action], [equipment/quality], [camera model], [resolution/clarity], [detail descriptors]
```

**Example (from reference):**
```
young Caucasian woman with highlight hair, sitting outside restaurant, wearing dress, rim lighting, studio lighting, looking at the camera, dslr, ultra quality, sharp focus, tack sharp, dof, film grain, Fujifilm XT3, crystal clear, 8K UHD, highly detailed glossy eyes, high detailed skin, skin pores
```

### Negative Prompt Formula
List artifacts, deformities, and unwanted styles separated by commas.

**Example:**
```
disfigured, ugly, bad, immature, cartoon, anime, 3d, painting, b&w
```

## Positive Prompt Construction Guidelines

### 1. Subject Description
Start with the primary subject and distinguishing characteristics.
- **Include:** Age, gender, ethnicity (if relevant), hair, eyes, build, pose
- **Be specific:** "young woman with wavy auburn hair and green eyes" vs "person"
- **Action/pose:** "sitting", "standing", "looking at camera", "mid-stride"

### 2. Setting & Background
Describe the environment and context.
- **Indoor/outdoor:** "restaurant patio", "forest clearing", "urban street"
- **Time/weather:** "golden hour", "rainy night", "misty morning"
- **Background elements:** "city skyline", "blurred trees", "brick wall"

### 3. Lighting
Lighting defines mood and visual quality.
- **Natural:** "golden hour sunlight", "soft window light", "overcast"
- **Studio:** "rim lighting", "butterfly lighting", "three-point setup"
- **Quality:** "soft light", "hard shadows", "dappled light"

### 4. Camera Equipment
Specify camera type and lens characteristics.
- **Camera type:** "DSLR", "mirrorless", "medium format", "smartphone"
- **Lens:** "50mm prime", "85mm portrait", "wide-angle", "telephoto"
- **Aperture:** "f/1.8 shallow depth of field", "f/8 deep focus"

### 5. Quality & Style Descriptors
Technical and aesthetic quality terms.
- **Resolution:** "8K UHD", "4K", "high resolution"
- **Clarity:** "crystal clear", "sharp focus", "tack sharp"
- **Film/Cinematic:** "film grain", "Kodak Portra 400", "cinematic", "anamorphic"
- **Photography style:** "photojournalistic", "fashion photography", "documentary"

### 6. Detail Enhancement
Add fine detail requests for realism.
- **Skin:** "highly detailed skin", "skin pores", "skin texture"
- **Eyes:** "glossy eyes", "catchlights", "detailed iris"
- **Hair:** "individual strands", "silky hair", "wind-swept"
- **Fabrics:** "fabric texture", "wrinkles", "folds"

### 7. Camera Model (Optional)
Specific camera models impart characteristic rendering.
- **Common:** "Fujifilm XT3", "Canon EOS R5", "Sony A7IV", "Hasselblad X2D"
- **Film cameras:** "Nikon F3", "Leica M6", "Pentax 67"

## Negative Prompt Construction Guidelines

Negative prompts suppress unwanted artifacts and styles. Common categories:

### 1. Anatomical Deformities
```
disfigured, deformed, malformed, mutated, extra limbs, missing limbs, asymmetric eyes, crossed eyes, bad anatomy, unnatural body
```

### 2. Quality Issues
```
blurry, low quality, jpeg artifacts, pixelated, noise, grainy, oversaturated, underexposed, overexposed, bad composition
```

### 3. Unwanted Art Styles
```
cartoon, anime, 3d, cgi, render, painting, drawing, sketch, illustration, watercolor, digital art, comic book
```

### 4. Incorrect Medium/Format
```
b&w, black and white, monochrome, sepia, vintage, hdr
```

### 5. Unrealistic Elements
```
fiction, fantasy, magical, unreal, unrealistic, robot, cyborg
```

### 6. Watermarks & Text
```
watermark, signature, text, logo, username, copyright
```

## Scenario-Based Examples

### Portrait Photography
```
Positive: 30-year-old woman with curly brown hair and hazel eyes, studio portrait, softbox lighting, Rembrandt lighting, looking directly at camera, Canon EOS R5, 85mm f/1.2, sharp focus, creamy bokeh, skin pores, detailed hair strands, professional headshot

Negative: deformed, ugly, bad anatomy, blurry, cartoon, anime, 3d, painting, watermark, text
```

### Landscape Photography
```
Positive: dramatic mountain landscape at sunrise, golden hour light, misty valleys, alpine lake reflection, Sony A7R IV, 24mm wide-angle, f/11, deep depth of field, ultra sharp, high dynamic range, detailed rock textures, National Geographic style

Negative: blurry, oversaturated, cartoon, painting, low quality, people, buildings, deformities
```

### Street Photography
```
Positive: candid street photography, man walking through rainy neon-lit Tokyo alley, wet pavement reflections, cinematic atmosphere, Fujifilm X100V, 35mm equivalent, film grain, Kodak Portra 400, moody, grainy, authentic moment

Negative: staged, posed, cartoon, 3d render, clean, oversharpened, bad lighting, watermark
```

### Product Photography
```
Positive: minimalist product shot of leather wallet on marble surface, studio lighting, soft shadows, top-down view, macro lens, Canon EOS R5, 100mm macro, f/2.8, tack sharp focus on wallet, texture detail, premium quality, commercial photography

Negative: blurry, dirty background, cartoon, 3d render, people hands, text, watermark, low quality
```

### Fashion Photography
```
Positive: fashion model in flowing silk dress, studio with dramatic rim lighting, high contrast, strong shadows, posing dynamically, Hasselblad X2D, 90mm medium format, film grain, Vogue style, high fashion, editorial look

Negative: casual, amateur, blurry, cartoon, anime, bad lighting, deformed, ugly
```

### Wildlife Photography
```
Positive: African lion in natural savanna habitat, golden hour sunlight, long grass foreground, Canon EOS R5 with 600mm telephoto, f/4, shallow depth of field, eye-level perspective, detailed fur texture, National Geographic quality, wildlife documentary

Negative: zoo, cage, blurry, cartoon, anime, deformed, bad anatomy, people, text
```

### Architectural Photography
```
Positive: modern glass skyscraper at twilight, city lights reflection, blue hour, wide-angle perspective, Sony A7R IV, 16mm, f/8, deep focus, architectural digest style, clean lines, glass reflections

Negative: distortion, fish-eye, blurry, cartoon, 3d render, sunset, bad exposure
```

### Food Photography
```
Positive: gourmet pasta dish in rustic Italian restaurant, overhead natural light, steam rising, shallow depth of field, 50mm prime, Fujifilm XT3, food photography, vibrant colors, texture of pasta, garnish detail, appetizing

Negative: ugly, unappetizing, blurry, cartoon, fake, plastic, text, watermark
```

## Optimization Tips for Stable Diffusion & Ollama

### General Principles
1. **Be descriptive but concise** — Too many conflicting descriptors reduce quality
2. **Prioritize key elements** — Lead with the most important subject/action
3. **Use established terminology** — Camera models, lighting terms, film stocks are recognized patterns
4. **Weight important terms** (Stable Diffusion): Use `(word:1.3)` syntax to emphasize

### Stable Diffusion Specific
- **Prompt length:** 75 tokens optimal; longer prompts may truncate
- **Token efficiency:** Remove filler words ("a", "the") if needed for space
- **Negative prompt essential:** Always include at least basic negatives (deformed, blurry, bad anatomy)
- **Artifacts to negate:** Add specific known SD issues: `nsfw, mutated hands, extra fingers`

### Ollama/Llama Considerations
- **Prompt complexity:** Longer descriptive prompts work well (60+ tokens acceptable)
- **Context window:** Be mindful of model's 8K context limit
- **Quality cues:** Ollama responds well to professional photography terms
- **Timeout handling:** Complex prompts may need 30-60 second timeouts

### Quality Keywords Hierarchy
**Essential (always include):**
- `sharp focus` / `tack sharp`
- `ultra quality` / `high quality`
- `detailed` / `highly detailed`

**Strongly recommended:**
- Camera/lens spec (`DSLR`, `85mm`, `f/1.8`)
- Lighting (`rim lighting`, `soft light`)
- Resolution (`8K UHD`, `high resolution`)
- Film/processing (`film grain`, `cinematic`)

**Contextual:**
- Camera model (`Fujifilm XT3`)
- Specific film stock (`Kodak Portra 400`)
- Style (`Vogue`, `National Geographic`)

### Avoid Overloading
Don't combine contradictory terms:
- ❌ `sharp focus` + `soft focus` — contradictory
- ❌ `cinematic` + `flat lighting` — mismatched
- ✅ Keep descriptors coherent

## Cheat Sheet

### Quick Reference Structure
```
Positive: [subject], [features], [setting], [lighting], [camera/lens], [quality], [details]
Negative: [deformities], [quality issues], [unwanted styles], [artifacts]
```

### Common Quality Stack (append to any prompt)
```
, sharp focus, tack sharp, ultra quality, highly detailed, crystal clear, 8K UHD, film grain
```

### Common Negative Stack (baseline for all prompts)
```
disfigured, deformed, ugly, bad anatomy, blurry, low quality, cartoon, anime, 3d, painting, watermark
```

### Camera Model Shortlist
- Portrait: Fujifilm XT3, Canon EOS R5, Sony A7IV
- Landscape: Sony A7R IV, Nikon Z8, Canon EOS R5
- Street: Fujifilm X100V, Leica Q3, Ricoh GR III
- Film emulation: Specify film stock instead of camera

## Best Practices Summary

1. **Lead with subject** — What is the image about?
2. **Add context** — Where/when is this happening?
3. **Specify lighting** — How is the scene lit?
4. **Call out tech specs** — Camera, lens, aperture
5. **Demand quality** — Sharpness, detail, resolution
6. **Request fine details** — Skin pores, hair strands, textures
7. **Exclude negatives** — Deformities, artifacts, wrong styles
8. **Keep it coherent** — All elements should work together stylistically

## Notes on Prompt Iteration
- Start with broad structure, refine with specific descriptors
- Test with variations; some terms work better with certain models
- Document successful prompt compositions for reuse
- For Stable Diffusion: Use prompt weighting `(keyword:1.2)` to emphasize
- For Ollama: Natural language works fine; no special syntax needed

## Instagram-Style Photo Generation

This section provides guidelines for generating Instagram-worthy photos based on a user-provided topic.

### Instagram Photo Characteristics
Instagram photos typically feature:
- **Aesthetic appeal** — Visually pleasing compositions with good lighting
- **Lifestyle focus** — Content that tells a story or conveys a mood
- **Warm, vibrant tones** — Slightly warm color grading, rich saturation
- **Shallow depth of field** — Subject isolation with soft backgrounds
- **Natural poses** — Candid or relaxed rather than formal
- **Trendy settings** — Coffee shops, travel destinations, urban scenes, nature spots

### Topic-Based Prompt Generation

When given a topic, generate Instagram-style prompts that:
1. **Center the topic** as the main subject or theme
2. **Add aesthetic context** — setting, props, styling
3. **Include Instagram-specific quality terms**
4. **Use warm, inviting lighting** — golden hour, soft natural light
5. **Add lifestyle/candid feel** — relaxed, authentic moments

### Instagram Prompt Template
```
[Topic as main subject], [aesthetic setting/location], [warm natural lighting], 
[smartphone photography style], [iPhone aesthetic], [shallow depth of field], 
[warm color tones], [lifestyle photography], [Instagram-worthy], [aesthetic composition], 
[highly detailed], [8K UHD], [natural colors], [professional quality]
```

### Instagram Negative Prompt
```
disfigured, deformed, ugly, bad anatomy, blurry, low quality, cartoon, anime, 3d, 
painting, watermark, text, logo, oversaturated, unnatural, staged, formal, b&w
```

### Instagram Photo Examples by Topic

#### Topic: "Coffee"
```
artisan latte art in ceramic cup, cozy coffee shop interior, warm golden hour sunlight through window, 
exposed brick wall background, smartphone photography, iPhone 15 Pro Max, shallow depth of field, 
warm color tones, lifestyle photography, Instagram-worthy, aesthetic flat lay composition, 
highly detailed foam art, steam rising, wooden table texture, morning vibes, 8K UHD
```

#### Topic: "Travel"
```
travel blogger at Santorini blue-domed church, golden hour sunset, whitewashed buildings, 
Aegean sea backdrop, flowing summer dress, candid laughing pose, smartphone camera, 
iPhone aesthetic, warm Mediterranean tones, shallow depth of field, travel lifestyle, 
Instagram influencer style, highly detailed, 8K UHD, wanderlust vibes
```

#### Topic: "Fitness"
```
fit woman in sportswear doing yoga at sunrise beach, ocean waves background, 
soft pink and orange sky, peaceful expression, active lifestyle, smartphone photography, 
iPhone 15 Pro, natural lighting, warm tones, fitness influencer aesthetic, 
shallow depth of field, highly detailed, 8K UHD, wellness vibes
```

#### Topic: "Food"
```
gourmet avocado toast breakfast plate, marble countertop, morning light, 
fresh herbs and poached eggs, smartphone food photography, iPhone aesthetic, 
top-down overhead shot, shallow depth of field, warm natural tones, 
Instagram food blogger style, highly detailed, 8K UHD, appetizing colors
```

#### Topic: "Fashion"
```
fashion influencer wearing trendy streetwear, urban city background with graffiti wall, 
golden hour lighting, confident pose, smartphone camera, iPhone aesthetic, 
warm color grading, shallow depth of field, fashion blog style, Instagram-worthy, 
highly detailed outfit details, 8K UHD, style content
```

### Instagram Prompt Quality Terms

**Essential Instagram Terms:**
- `smartphone photography`
- `iPhone aesthetic`
- `Instagram-worthy`
- `lifestyle photography`
- `aesthetic composition`
- `warm color tones`

**Recommended:**
- `shallow depth of field`
- `golden hour`
- `natural lighting`
- `candid pose`
- `influencer style`
- `highly detailed`

**Optional Enhancement:**
- `golden gate glow`
- `morning light`
- `soft shadows`
- `film-like quality`
- `clean aesthetic`
- `minimalist composition`

### Best Practices for Instagram Prompts

1. **Always include smartphone/iPhone terms** — Sets the aesthetic style
2. **Use "Instagram-worthy" explicitly** — Signals the target platform
3. **Add warm color tones** — Signature Instagram look
4. **Include lifestyle context** — Makes the photo relatable
5. **Use shallow depth of field** — Professional smartphone look
6. **Keep subjects natural and candid** — Authentic feel
7. **Specify aesthetic settings** — Coffee shops, beaches, urban spots work well
8. **Request high detail** — 8K UHD, highly detailed for quality
