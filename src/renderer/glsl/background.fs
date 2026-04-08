#version 330 core
in  vec2 fragTexCoord;
in  vec3 fragPos;
out vec4 finalColor;

uniform vec2  resolution;
uniform vec2  mouse;
uniform float time;

float hash(vec2 p) {
    p = fract(p * vec2(127.1, 311.7));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

float hash3(vec3 p) {
    p = fract(p * vec3(127.1, 311.7, 74.7));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y + p.y * p.z);
}

float star(vec2 uv, vec2 pos, float size, float twinkle) {
    float d = length(uv - pos);
    float b = size / (d * 900.0 + size);
    b *= 0.6 + 0.4 * sin(time * twinkle + hash(pos) * 6.28318);
    return b;
}

// Projection sphérique -> UV 2D à partir de la direction 3D
vec2 sphereUV(vec3 dir) {
    vec3 d = normalize(dir);
    float u = 0.5 + atan(d.z, d.x) / (2.0 * 3.14159265);
    float v = 0.5 - asin(clamp(d.y, -1.0, 1.0)) / 3.14159265;
    return vec2(u, v);
}

vec2 blackhole(vec2 uv, vec2 center, float radius, float mdist) {
    vec2  delta = uv - center;
    float dist  = length(delta);
    float infl  = radius * (1.0 + 0.5 * (1.0 - clamp(mdist / 0.3, 0.0, 1.0)));
    float dark  = 1.0 - smoothstep(0.0, infl * 0.55, dist);
    float ring  = smoothstep(infl * 0.55, infl * 0.62, dist)
                * smoothstep(infl * 1.15, infl * 0.78, dist);
    return vec2(dark, ring);
}

void main() {
    // UV sphériques depuis la direction 3D du fragment (skybox)
    vec2 uv  = sphereUV(fragPos);
    vec2 muv = mouse;

    // --- fond dégradé espace ------------------------------------------------
    vec3 col = mix(vec3(0.01, 0.01, 0.05), vec3(0.04, 0.02, 0.10), uv.y);

    // nébuleuse douce qui suit la souris
    float neb = exp(-length(uv - muv) * 3.5) * 0.20;
    col += vec3(0.10, 0.02, 0.18) * neb;
    // nébuleuse secondaire fixe
    float neb2 = exp(-length(uv - vec2(0.6, 0.3)) * 5.0) * 0.12;
    col += vec3(0.0, 0.05, 0.20) * neb2;

    // --- étoiles grille fine ------------------------------------------------
    float stars = 0.0;
    float gs = 40.0;
    vec2 cell = floor(uv * gs);
    for (int dx = -1; dx <= 1; dx++) {
        for (int dy = -1; dy <= 1; dy++) {
            vec2  c = cell + vec2(float(dx), float(dy));
            float h = hash(c);
            if (h > 0.50) {
                vec2  pos  = (c + vec2(fract(h * 37.1), fract(h * 19.3))) / gs;
                float size = 0.04 + (h - 0.50) * 0.9;
                stars += star(uv, pos, size, 0.8 + h * 2.5);
            }
        }
    }
    // grandes étoiles brillantes
    for (int i = 0; i < 14; i++) {
        float fi   = float(i);
        vec2  seed = vec2(fi * 0.173 + 0.03, fi * 0.251 + 0.07);
        vec2  pos  = vec2(fract(seed.x * 7.13 + seed.y * 3.17),
                          fract(seed.x * 2.79 + seed.y * 9.43));
        float size = 0.3 + hash(seed) * 1.6;
        stars += star(uv, pos, size, 1.2 + hash(seed + 0.5) * 3.0);
    }
    col += clamp(stars, 0.0, 1.0) * vec3(0.88, 0.93, 1.0);

    // --- trous noirs --------------------------------------------------------
    vec2 bh1c   = vec2(0.20, 0.35) + (muv - 0.5) * 0.05;
    vec2 bh1    = blackhole(uv, bh1c,  0.085, length(muv - bh1c));
    vec2 bh2c   = vec2(0.75, 0.58) + (muv - 0.5) * 0.025;
    vec2 bh2    = blackhole(uv, bh2c,  0.065, length(muv - bh2c));
    vec2 bh3c   = mix(vec2(0.50, 0.72), muv, 0.15);
    vec2 bh3    = blackhole(uv, bh3c,  0.040, length(muv - bh3c));

    col += bh1.y * vec3(0.55, 0.20, 1.00) * 2.8;
    col += bh2.y * vec3(0.90, 0.45, 0.10) * 2.2;
    col += bh3.y * vec3(0.15, 0.80, 1.00) * 2.0;

    float darkness = max(max(bh1.x, bh2.x), bh3.x);
    col *= 1.0 - darkness * 0.97;

    finalColor = vec4(clamp(col, 0.0, 1.0), 1.0);
}
