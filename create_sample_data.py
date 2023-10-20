import numpy as np
import matplotlib.pyplot as plt

##### Cuboid data
'''
# test on 2D square
spectral_index = -2 # P(k) ~ k**spectral_index
Nx = 128
Ny = Nx
res = 1.0
Lx = Nx * res
Ly = Ny * res

kx1d = np.fft.fftfreq(Nx) * 2 * np.pi / Lx
ky1d = np.fft.fftfreq(Ny) * 2 * np.pi / Ly
kx, ky = np.meshgrid(kx1d, ky1d, indexing='ij')
kmag = np.sqrt(kx**2 + ky**2)
amplitude = kmag**(spectral_index / 2.0)
amplitude[kmag == 0] = 0
phase = np.random.random(amplitude.shape) * np.pi * 2
rho = np.real(np.fft.ifftn(amplitude * np.exp(1j * phase)))

plt.imshow(rho, aspect='equal')
plt.colorbar()
plt.show()


# test on 2D rectangle
spectral_index = -2 # P(k) ~ k**spectral_index
Nx = 128
Ny = 256
res = 1.0
Lx = Nx * res
Ly = Ny * res

kx1d = np.fft.fftfreq(Nx) * 2 * np.pi / Lx
ky1d = np.fft.fftfreq(Ny) * 2 * np.pi / Ly
kx, ky = np.meshgrid(kx1d, ky1d, indexing='ij')
kmag = np.sqrt(kx**2 + ky**2)
amplitude = kmag**(spectral_index / 2.0)
amplitude[kmag == 0] = 0
phase = np.random.random(amplitude.shape) * np.pi * 2
rho = np.real(np.fft.ifftn(amplitude * np.exp(1j * phase)))

plt.imshow(rho, aspect='equal')
plt.colorbar()
plt.show()
'''

# Generate for 3D cube
spectral_index = -1.8 # P(k) ~ k**spectral_index
Nx = 64
Ny = 64
Nz = 64
res = 1.0
Lx = Nx * res
Ly = Ny * res
Lz = Nz * res

kx1d = np.fft.fftfreq(Nx) * 2 * np.pi / Lx
ky1d = np.fft.fftfreq(Ny) * 2 * np.pi / Ly
kz1d = np.fft.fftfreq(Nz) * 2 * np.pi / Lz
kx, ky, kz = np.meshgrid(kx1d, ky1d, kz1d, indexing='ij')
kmag = np.sqrt(kx**2 + ky**2 + kz**2)
amplitude = kmag**(spectral_index / 2.0)
amplitude[kmag == 0] = 0
phase = np.random.random(amplitude.shape) * np.pi * 2
rho = 15 * np.real(np.fft.ifftn(amplitude * np.exp(1j * phase)))
rho = np.clip(1 + rho, 0, None)
print(np.quantile(rho, [0.01, 0.5, 0.99]), rho.min(), rho.max())

plt.imshow(rho.mean(axis=2), aspect='equal')
plt.colorbar()
plt.show()

np.savez('cube_cosmo.npz', arr3d = rho, spectral_index = spectral_index, extent = np.array([[0,Lx], [0,Ly], [0,Lz]]),
         metadata = '3D array of shape (Nx, Ny, Nz) containing (1 + ) a gaussian random field with spectral_index, approximating a cosmological density field between extent.')

# Generate for 3D cube
spectral_index = -1.8 # P(k) ~ k**spectral_index
Nx = 64
Ny = 128
Nz = 32
res = 1.0
Lx = Nx * res
Ly = Ny * res
Lz = Nz * res

kx1d = np.fft.fftfreq(Nx) * 2 * np.pi / Lx
ky1d = np.fft.fftfreq(Ny) * 2 * np.pi / Ly
kz1d = np.fft.fftfreq(Nz) * 2 * np.pi / Lz
kx, ky, kz = np.meshgrid(kx1d, ky1d, kz1d, indexing='ij')
kmag = np.sqrt(kx**2 + ky**2 + kz**2)
amplitude = kmag**(spectral_index / 2.0)
amplitude[kmag == 0] = 0
phase = np.random.random(amplitude.shape) * np.pi * 2
rho = 15 * np.real(np.fft.ifftn(amplitude * np.exp(1j * phase)))
rho = np.clip(1 + rho, 0, None)
print(np.quantile(rho, [0.01, 0.5, 0.99]), rho.min(), rho.max())

plt.imshow(rho.mean(axis=2), aspect='equal')
plt.colorbar()
plt.show()

np.savez('cuboid_cosmo.npz', arr3d = rho, spectral_index = spectral_index, extent = np.array([[0,Lx], [0,Ly], [0,Lz]]),
         metadata = '3D array of shape (Nx, Ny, Nz) containing (1 + ) a gaussian random field with spectral_index, approximating a cosmological density field between extent.')

##### Spherical data
Nr = 32
Ntheta = 64
Nphi = 128
R = 1.0
theta = np.linspace(0, np.pi, Ntheta).reshape(-1,1)
phi = np.arange(0, 2 * np.pi, 2 * np.pi / Nphi).reshape(1,-1)
r = np.linspace(R / Nr, R, Nr)
phi0 = r * 4 * np.pi # 2 rounds till R
amplitude = 1 / r
h_plus = np.zeros((Ntheta, Nphi, Nr))
h_cross = np.zeros((Ntheta, Nphi, Nr))
for i, (p0, a) in enumerate(zip(phi0, amplitude)):
    h_plus[:,:,i] = a * (1 + np.cos(theta)**2) * np.cos(2 * (phi - p0))
    h_cross[:,:,i] = a * np.cos(theta) * np.sin(2 * (phi - p0))
    '''
    plt.imshow(h_plus[:,:,i])
    plt.colorbar()
    plt.show()
    
    plt.imshow(h_cross[:,:,i])
    plt.colorbar()
    plt.show()
    '''

np.savez('sphere_GW22+.npz', arr3d = h_plus, theta = theta, phi = phi, r = r,
         metadata = '3D array of shape (Ntheta, Nphi, Nr) containing the amplitude of the + polarization of the leading order GWs emitted by a circular binary.')
np.savez('sphere_GW22x.npz', arr3d = h_cross, theta = theta, phi = phi, r = r,
         metadata = '3D array of shape (Ntheta, Nphi, Nr) containing the amplitude of the x polarization of the leading order GWs emitted by a circular binary.')
