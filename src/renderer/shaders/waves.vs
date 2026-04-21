#version 330

in vec3 vertexPosition;
in vec2 vertexTexCoord;

uniform mat4 mvp;
uniform float uTime;
uniform float uAmplitude;

out float vHeight;


float hash(vec2 p)
{
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p)
{
    vec2 i = floor(p);
    vec2 f = fract(p);

    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));

    vec2 u = f * f * (3.0 - 2.0 * f);

    return mix(a, b, u.x) +
           (c - a) * u.y * (1.0 - u.x) +
           (d - b) * u.x * u.y;
}

void main()
{
    vec3 pos = vertexPosition;

    vec2 warped = vec2(
        pos.x + sin(pos.z * 0.6 + uTime * 0.7) * 0.4,
        pos.z + cos(pos.x * 0.6 + uTime * 0.5) * 0.4
    );

    float wave1 = sin(warped.x * 1.2 + uTime);
    float wave2 = cos(warped.y * 1.4 + uTime * 0.8);
    float wave3 = sin((warped.x + warped.y) * 0.7 + uTime * 1.3);

    float n = noise(warped * 0.8);

    float wave = (wave1 + wave2 * 0.7 + wave3 * 0.5) / 2.2;
    wave += n * 0.25;

    pos.y += wave * uAmplitude;

    vHeight = wave;

    gl_Position = mvp * vec4(pos, 1.0);
}