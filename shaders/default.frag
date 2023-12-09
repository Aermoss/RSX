#version 460 core

in vec2 fragTexCoords;
uniform vec3 color;
uniform sampler2D tex;

void main() {
    gl_FragColor = texture(tex, fragTexCoords);
}