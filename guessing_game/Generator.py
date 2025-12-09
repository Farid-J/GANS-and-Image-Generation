import torch
import torch.nn as nn
from torchvision.utils import save_image
import os


# ---------------------------------------
#  DCGAN Generator (Your Exact Code)
# ---------------------------------------

class Generator(nn.Module):
    def __init__(self, z_dim):
        super().__init__()
        self.main = nn.Sequential(
            nn.ConvTranspose2d(z_dim, 512, 4, 1, 0, bias=False),
            nn.BatchNorm2d(512),
            nn.ReLU(True),

            nn.ConvTranspose2d(512, 256, 4, 2, 1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(True),

            nn.ConvTranspose2d(256, 128, 4, 2, 1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(True),

            nn.ConvTranspose2d(128, 64, 4, 2, 1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(True),

            nn.ConvTranspose2d(64, 3, 4, 2, 1, bias=False),
            nn.Tanh(),
        )

    def forward(self, z):
        return self.main(z)


# ---------------------------------------
#  Generate Flower Images Locally
# ---------------------------------------

def generate_samples(generator_path="generator.pth", 
                     num_images=8, 
                     z_dim=100, 
                     out_dir="generated_flowers"):

        # Create output folder
        os.makedirs(out_dir, exist_ok=True)

        # CPU/GPU choice (desktop friendly)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print("Using device:", device)

        # Load generator
        gen = Generator(z_dim).to(device)
        gen.load_state_dict(torch.load(generator_path, map_location=device))
        gen.eval()

        # Create noise vectors
        z = torch.randn(num_images, z_dim, 1, 1, device=device)

        # Generate fake flowers
        with torch.no_grad():
            fake_imgs = gen(z)

        # Save each image
        for i, img in enumerate(fake_imgs):
            save_image(img, f"{out_dir}/flower_{i}.png", normalize=True)

        print(f"Saved {num_images} images → {out_dir}/")


# ---------------------------------------
#  Run the generator
# ---------------------------------------

if __name__ == "__main__":
    generate_samples(
        generator_path="generator.pth",  # <-- your model path
        num_images=12,
        z_dim=100
    )
