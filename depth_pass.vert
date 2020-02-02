#version 420

layout (location = 0) in vec4 in_position;

uniform mat4 LightProjectionModelview;

void main() {
  gl_Position = LightProjectionModelview * in_position;
}
  
