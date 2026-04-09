// #version 330 core

// in vec3 vertexPosition;
// in vec2 vertexTexCoord;

// out vec2 fragTexCoord;
// out vec3 fragPos;

// uniform mat4 matProjection;
// uniform mat4 matView;

// void main() {
//     fragTexCoord = vertexTexCoord;
//     fragPos      = vertexPosition;

//     mat4 rotView = mat4(mat3(matView));
//     vec4 clipPos = matProjection * rotView * vec4(vertexPosition, 1.0);

//     gl_Position = clipPos.xyww;
// }

#version 330 core

in vec3 vertexPosition;

out vec3 fragTexCoord;   // vec3 for cubemap sampling, not vec2!

uniform mat4 matProjection;
uniform mat4 matView;

void main()
{
    fragTexCoord = vertexPosition;  // use position as cubemap direction

    mat4 rotView = mat4(mat3(matView));  // strip translation
    vec4 clipPos = matProjection * rotView * vec4(vertexPosition, 1.0);
    gl_Position  = clipPos.xyww;
}
