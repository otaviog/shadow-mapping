#version 420

in VertexOut {
  vec3 pos;
  vec3 normal;
  vec4 pos_light_space;
}
vout;

uniform sampler2DRectShadow ShadowMap;
uniform mat4 Modelview;
uniform vec3 LightPos;

uniform vec3 AmbientColor;
uniform vec3 DiffuseColor;
uniform vec3 SpecularColor;
uniform float SpecularExp;

float get_shadowing(vec4 pos_light_space, vec3 normal, vec3 light_dir) {
  vec3 proj = pos_light_space.xyz / pos_light_space.w;
  proj = proj * 0.5 + 0.5;
  proj.x *= 2048;
  proj.y *= 2048;
  float bias = max(4e-5 * (1.0 - dot(normal, light_dir)), 5e-6);

  proj.z -= bias;

  float shadow_sum = 0.0;
  for (int r = -2; r <= 2; ++r) {
    for (int c = -2; c <= 2; ++c) {
      vec3 pcf_coord = vec3(proj.xy + vec2(c, r), proj.z);
      float shadow = texture(ShadowMap, pcf_coord).r;
      shadow_sum += shadow;
    }
  }

  return shadow_sum / 25.0;
}

out vec4 frag_color;

void main() {
  vec3 light_pos = (Modelview * vec4(LightPos, 1)).xyz;
  vec3 light_dir = normalize(light_pos - vout.pos);

  float shadow = get_shadowing(vout.pos_light_space, vout.normal, light_dir);

  vec3 final_color = AmbientColor;

  float diffuse_factor = max(dot(light_dir, vout.normal), 0);
  final_color += diffuse_factor * DiffuseColor;

  vec3 view_dir = normalize(-vout.pos);
  vec3 refraction_dir =
      2 * dot(vout.normal, light_dir) * vout.normal - light_dir;

  float specular_factor =
	min(pow(max(dot(view_dir, refraction_dir), 0), SpecularExp), 1);
  final_color += specular_factor * SpecularColor;

  final_color *= max(shadow, 0.2);

  frag_color = vec4(final_color, 1);
}
