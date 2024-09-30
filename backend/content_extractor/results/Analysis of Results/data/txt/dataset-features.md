# 3.1.4.4 Dataset Features

| Feature | Options | What | Why |
|---------|---------|------|-----|
| image_quality | high, medium, low | The overall clarity and resolution of the image | Assesses how OCR performance varies with image quality, which is crucial in real-world applications |
| watermark_present | yes, no | Presence of a watermark or background text | Evaluates OCR robustness against interference from non-primary text elements |
| image_source | digital, foto, scan | The origin or method of image creation | Tests OCR effectiveness across different image acquisition methods, simulating various real-world scenarios |
| color_mode | color, b/w | Whether the image is in color or black and white | Determines if color information impacts OCR accuracy and if models perform differently on monochrome vs. color images |
| content_type | Number-heavy, Tabular-heavy, Text-heavy, Text-heavy (no numbers) | The predominant type of content in the image | Assesses OCR performance across different types of document layouts and content, which may require different processing approaches |
| rotation_angle | 0° to 360° | The degree of rotation applied to the image | Tests the OCR system's ability to handle text at various orientations, simulating real-world document misalignments |
| language | EN, ES | The primary language of the text in the image | Evaluates the OCR system's language capabilities and potential biases across different scripts |
| gold_standard | yes, no | Whether the image has been manually verified for accuracy | Provides a benchmark for assessing OCR performance against human-verified data |
| ready_for_processing | yes, no | Indicates if the image meets all criteria for inclusion in the study | Ensures only valid, prepared samples are included in the analysis |

This diverse set of features allows for a comprehensive evaluation of OCR performance across a wide range of image characteristics and conditions.
