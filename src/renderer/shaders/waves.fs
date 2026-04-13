#version 330

in float vHeight;
out vec4 finalColor;

void main()
{
    vec3 deepBlue = vec3(0.0, 0.2, 0.5);
    vec3 lightBlue = vec3(0.0, 0.5, 0.8);
    vec3 white = vec3(1.0);

    float h = vHeight * 0.5 + 0.5;
    vec3 color = mix(deepBlue, lightBlue, h);

    // crest (white tips)
    float crest = smoothstep(0.2, 0.25, vHeight);
    color = mix(color, white, crest);

	float noise = fract(sin(vHeight * 20.0) * 100.0);
	crest *= noise;

    finalColor = vec4(color, 1.0);
}