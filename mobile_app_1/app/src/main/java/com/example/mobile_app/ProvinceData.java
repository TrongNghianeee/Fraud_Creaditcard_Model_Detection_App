package com.example.mobile_app;

import java.util.HashMap;
import java.util.Map;

/**
 * Province/City population data for Vietnam
 * Contains 63 provinces and cities with their population
 */
public class ProvinceData {
    
    private static final Map<String, Long> PROVINCE_POPULATION = new HashMap<>();
    
    static {
        // Major cities
        PROVINCE_POPULATION.put("ha noi", 8054000L);
        PROVINCE_POPULATION.put("hanoi", 8054000L);
        PROVINCE_POPULATION.put("ho chi minh", 8993000L);
        PROVINCE_POPULATION.put("hcm", 8993000L);
        PROVINCE_POPULATION.put("hai phong", 2028900L);
        PROVINCE_POPULATION.put("da nang", 1134300L);
        PROVINCE_POPULATION.put("can tho", 1282100L);
        
        // Provinces (A-D)
        PROVINCE_POPULATION.put("an giang", 2163000L);
        PROVINCE_POPULATION.put("ba ria vung tau", 1148300L);
        PROVINCE_POPULATION.put("bac giang", 1803950L);
        PROVINCE_POPULATION.put("bac kan", 313905L);
        PROVINCE_POPULATION.put("bac lieu", 907236L);
        PROVINCE_POPULATION.put("bac ninh", 1368840L);
        PROVINCE_POPULATION.put("ben tre", 1288029L);
        PROVINCE_POPULATION.put("binh dinh", 1501800L);
        PROVINCE_POPULATION.put("binh duong", 2426561L);
        PROVINCE_POPULATION.put("binh phuoc", 1052200L);
        PROVINCE_POPULATION.put("binh thuan", 1230559L);
        PROVINCE_POPULATION.put("ca mau", 1217100L);
        PROVINCE_POPULATION.put("cao bang", 531197L);
        PROVINCE_POPULATION.put("dak lak", 1912759L);
        PROVINCE_POPULATION.put("dak nong", 613925L);
        PROVINCE_POPULATION.put("dien bien", 563282L);
        PROVINCE_POPULATION.put("dong nai", 3097107L);
        PROVINCE_POPULATION.put("dong thap", 1676300L);
        
        // Provinces (G-L)
        PROVINCE_POPULATION.put("gia lai", 1513847L);
        PROVINCE_POPULATION.put("ha giang", 854679L);
        PROVINCE_POPULATION.put("ha nam", 820700L);
        PROVINCE_POPULATION.put("ha tinh", 1288866L);
        PROVINCE_POPULATION.put("hai duong", 1892008L);
        PROVINCE_POPULATION.put("hau giang", 769700L);
        PROVINCE_POPULATION.put("hoa binh", 854131L);
        PROVINCE_POPULATION.put("hung yen", 1282400L);
        PROVINCE_POPULATION.put("khanh hoa", 1231107L);
        PROVINCE_POPULATION.put("kien giang", 1837000L);
        PROVINCE_POPULATION.put("kon tum", 530944L);
        PROVINCE_POPULATION.put("lai chau", 460196L);
        PROVINCE_POPULATION.put("lam dong", 1296906L);
        PROVINCE_POPULATION.put("lang son", 788100L);
        PROVINCE_POPULATION.put("lao cai", 731050L);
        PROVINCE_POPULATION.put("long an", 1688000L);
        
        // Provinces (N-Q)
        PROVINCE_POPULATION.put("nam dinh", 1780393L);
        PROVINCE_POPULATION.put("nghe an", 3327791L);
        PROVINCE_POPULATION.put("ninh binh", 983400L);
        PROVINCE_POPULATION.put("ninh thuan", 590467L);
        PROVINCE_POPULATION.put("phu tho", 1477600L);
        PROVINCE_POPULATION.put("phu yen", 877200L);
        PROVINCE_POPULATION.put("quang binh", 913160L);
        PROVINCE_POPULATION.put("quang nam", 1495200L);
        PROVINCE_POPULATION.put("quang ngai", 1263052L);
        PROVINCE_POPULATION.put("quang ninh", 1320324L);
        PROVINCE_POPULATION.put("quang tri", 635918L);
        
        // Provinces (S-Y)
        PROVINCE_POPULATION.put("soc trang", 1301950L);
        PROVINCE_POPULATION.put("son la", 1248415L);
        PROVINCE_POPULATION.put("tay ninh", 1172500L);
        PROVINCE_POPULATION.put("thai binh", 1860447L);
        PROVINCE_POPULATION.put("thai nguyen", 1288000L);
        PROVINCE_POPULATION.put("thanh hoa", 3689000L);
        PROVINCE_POPULATION.put("thua thien hue", 1157829L);
        PROVINCE_POPULATION.put("tien giang", 1738800L);
        PROVINCE_POPULATION.put("tra vinh", 1015300L);
        PROVINCE_POPULATION.put("tuyen quang", 784811L);
        PROVINCE_POPULATION.put("vinh long", 1023400L);
        PROVINCE_POPULATION.put("vinh phuc", 1152888L);
        PROVINCE_POPULATION.put("yen bai", 827654L);
    }
    
    /**
     * Get population for a given city/province name
     * 
     * @param cityName City/province name (case-insensitive, Vietnamese without diacritics)
     * @return Population count, or 0 if not found
     */
    public static long getPopulation(String cityName) {
        if (cityName == null || cityName.trim().isEmpty()) {
            return 0;
        }
        
        String normalizedCity = cityName.toLowerCase().trim();
        return PROVINCE_POPULATION.getOrDefault(normalizedCity, 0L);
    }
    
    /**
     * Check if a city/province name is valid
     * 
     * @param cityName City/province name
     * @return true if valid, false otherwise
     */
    public static boolean isValidCity(String cityName) {
        if (cityName == null || cityName.trim().isEmpty()) {
            return false;
        }
        
        String normalizedCity = cityName.toLowerCase().trim();
        return PROVINCE_POPULATION.containsKey(normalizedCity);
    }
    
    /**
     * Get all province/city names
     * 
     * @return Map of all provinces with their populations
     */
    public static Map<String, Long> getAllProvinces() {
        return new HashMap<>(PROVINCE_POPULATION);
    }
}
