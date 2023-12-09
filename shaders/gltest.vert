#version 460

layout (location = 0) in vec3 position;
layout (location = 1) in vec2 texCoord;
layout (location = 2) in vec3 normal;

uniform mat4 proj;
uniform mat4 view;
uniform mat4 model;

void main() {
    gl_Position = proj * view * model * vec4(position, 1.0f);
}