import React from 'react';
import HeaderWhite from "./Header_white.js";
import { COMPANY_NAME } from "../../utils/constants.js";
import { Link } from 'react-router-dom';
import '../../css/Terms.css';

const CGV = () => {
  return (
    <div>
      <HeaderWhite/>
        <div className="terms-container">
            <h1>Conditions Générales de Vente</h1>

            <h2>1. Introduction</h2>
            <p>
                Les présentes Conditions Générales de Vente (ci-après "CGV") régissent les ventes de produits et services réalisés
                par { COMPANY_NAME } via la Plateforme. En passant commande sur la Plateforme, vous acceptez les présentes CGV.
            </p>

            <h2>2. Produits et Services</h2>
            <p>
                Les descriptions, illustrations et prix des produits et services proposés sur la Plateforme sont aussi précis que
                possible. Toutefois, { COMPANY_NAME } ne garantit pas l'absence d'erreurs ou de modifications.
            </p>

            <h2>3. Commandes</h2>
            <p>
                Les commandes passées sur la Plateforme engagent le client dès leur validation. { COMPANY_NAME } se réserve le
                droit de refuser toute commande pour des motifs légitimes.
            </p>

            <h2>4. Prix et Paiement</h2>
            <p>
                Les prix des produits et services sont indiqués en euros, toutes taxes comprises. Le paiement est exigible
                immédiatement à la commande. Les modes de paiement acceptés sont indiqués sur la Plateforme.
            </p>

            <h2>5. Livraison</h2>
            <p>
                Les produits sont livrés à l'adresse indiquée lors de la commande. Les délais de livraison sont donnés à titre
                indicatif et peuvent varier. { COMPANY_NAME } ne peut être tenue responsable des retards de livraison.
            </p>

            <h2>6. Rétractation et Retour</h2>
            <p>
                Conformément au Code de la consommation, vous disposez d'un délai de 14 jours pour exercer votre droit de
                rétractation. Les produits doivent être retournés dans leur état d'origine et les frais de retour sont à la charge
                du client.
            </p>

            <h2>7. Garantie</h2>
            <p>
                Les produits bénéficient de la garantie légale de conformité et de la garantie contre les vices cachés. En cas de
                non-conformité ou de défaut, vous pouvez retourner les produits pour réparation, remplacement ou remboursement.
            </p>

            <h2>8. Responsabilité</h2>
            <p>
                { COMPANY_NAME } ne saurait être tenue responsable des dommages indirects résultant de l'achat de produits ou
                services sur la Plateforme. La responsabilité de { COMPANY_NAME } est limitée au montant de la commande.
            </p>

            <h2>9. Droit Applicable et Juridiction Compétente</h2>
            <p>
                Les présentes CGV sont régies par le droit français. Tout litige relatif à l'interprétation ou à l'exécution des
                présentes CGV sera soumis à la compétence exclusive des tribunaux français.
            </p>

            <h2>10. Contact</h2>
            <p>
                Pour toute question concernant les présentes CGV, vous pouvez nous contacter à <Link to="/contact">nous contacter</Link>.
            </p>
        </div>
    </div>
  );
};

export default CGV;