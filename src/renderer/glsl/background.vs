#version 330 core
in vec3 vertexPosition;
in vec2 vertexTexCoord;
out vec2 fragTexCoord;
out vec3 fragPos;
uniform mat4 matProjection;
uniform mat4 matView;

void main() {
    fragTexCoord = vertexTexCoord;
    fragPos      = vertexPosition;
    // Supprime la translation : skybox reste "infinie"
    mat4 rotView = mat4(mat3(matView));
    vec4 clipPos = matProjection * rotView * vec4(vertexPosition, 1.0);
    // Force depth = 1.0 (toujours derrière tout)
    gl_Position = clipPos.xyww;
}
