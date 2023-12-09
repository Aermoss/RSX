#version 460 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec2 texCoords;

out vec2 fragTexCoords;
uniform mat4 matrix;

void main() {
    fragTexCoords = texCoords;
    gl_Position = matrix * vec4(position, 1.0f);
}