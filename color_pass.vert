#version 420

layout (location = 0) in vec4 in_position;
layout (location = 1) in vec3 in_normal;

out VertexOut {
  vec3 pos;
  vec3 normal;
  vec4 pos_light_space;
} vout;

uniform mat4 Modelview;
uniform mat4 ProjectionModelview;
uniform mat3 NormalModelview;
uniform mat4 LightProjectionModelview;

void main() {
  gl_Position = ProjectionModelview*in_position;
  
  vout.pos = (Modelview*in_position).xyz;
  //vout.pos = in_position.xyz;
  vout.normal = normalize(NormalModelview*in_normal);
  
  vout.pos_light_space = LightProjectionModelview*in_position;
}
