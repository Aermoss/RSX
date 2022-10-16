include "rsxmath" : *;

float circle_area(float radius) {
    return std::pi * std::pow(radius, 2);
}

float circle_circumference(float radius) {
    return std::pi * radius * 2;
}

float hypotenuse(float a, float b) {
    return std::sqrt(std::pow(a, 2) + std::pow(b, 2));
}